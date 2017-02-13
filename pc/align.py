# -*- coding: utf-8 -*-
"""
Description: Text aligning
"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

import os
import logging
import tempfile
import shutil
import subprocess
import pymongo
import traceback
from multiprocessing import Pool
from yalign import YalignModel
from yalign import text_to_document
from .filestorage import FileStorage
from .text import remove_extra_spaces
from converter import tokenizer
from converter import detokenizer

log = logging.getLogger(__name__)
model = None
hunalign_path = os.path.join(os.path.dirname(__file__), 'hunalign')
detokenizer_script = os.path.join(os.path.dirname(__file__), 'detokenizer.perl')

def _init_model(model_name, mode):
    """@todo: Docstring for _init_model.

    :model_name: @todo
    :returns: @todo

    """
    global model
    model = YalignModel.load(model_name)
    model.mode = mode

def _iter_text(col, lang1, lang2):
    lang_id = '-'.join((lang1, lang2))
    query = {
        'lang': lang1,
        'text': {'$exists': True},
        'done_align': {'$ne': lang_id}
    }
    for art1 in col.find(query, no_cursor_timeout=True):
        query = {'uid': art1['uid'], 'lang': lang1}
        update = {'$set': {'done_align': lang_id}}
        col.update(query, update)
        art2 = col.find_one(dict(uid=art1['uid'], lang=lang2))
        if not art2:
            continue
        if art1.get('text', None) and art2.get('text', None):
            yield (art1, art2)

def _align_text(art_pair):
    art1, art2 = art_pair
    try:
        doc1 = text_to_document(remove_extra_spaces(art1['text']))
        doc2 = text_to_document(remove_extra_spaces(art2['text']))
        pairs = model.align(doc1, doc2)
    except:
        return None
    else:
        pairs = [(p[0].to_text(), p[1].to_text()) for p in pairs]
        text1 = [p[0] for p in pairs]
        text1 = [t+'\n' for t in text1]
        text1 = ''.join(text1)
        text2 = [p[1] for p in pairs]
        text2 = [t+'\n' for t in text2]
        text2 = ''.join(text2)
    return (text1, text2)

def _align_text_with_hunalign(art_pair):
    """TODO: Docstring for _align_text_with_hunalign.

    :art_pair: TODO
    :returns: TODO

    """
    art1, art2 = art_pair
    text1 = remove_extra_spaces(art1['text'])
    text2 = remove_extra_spaces(art2['text'])
    try:
        tempdir = tempfile.mkdtemp()
        path1 = os.path.join(tempdir, '1')
        path2 = os.path.join(tempdir, '2')
        with open(path1, 'w') as f:
            f.write(text1.encode('utf-8'))
        with open(path2, 'w') as f:
            f.write(text2.encode('utf-8'))
        tokenizer.convert_dir_in_place(tempdir)
        result = subprocess.check_output([
            hunalign_path,
            '-text',
            '-utf',
            '/dev/null',
            path1,
            path2
        ])
        sentences = []
        result = result.decode('utf-8')
        for rec in result.split('\n'):
            tokens = rec.split('\t')
            if len(tokens) == 3:
                sentences.append((tokens[0], tokens[1]))
        # no need to save empty file
        if not sentences:
            return None
        # filter and strip
        sentences = [
            (s1.strip(u'\t\n\r\f\v \ufeff'),
                s2.strip(u'\t\n\r\f\v \ufeff'))
            for s1, s2 in sentences
        ]
        sentences = [(s1, s2) for s1, s2 in sentences
                        if s1 and s2 and not s1 == s2]
        text1 = u'\n'.join(s1 for s1, _ in sentences)
        text2 = u'\n'.join(s2 for _, s2 in sentences)
        with open(path1, 'w') as f:
            f.write(text1.encode('utf-8'))
        with open(path2, 'w') as f:
            f.write(text2.encode('utf-8'))
        detokenizer.convert_dir_in_place(detokenizer_script, tempdir)
        with open(path1, 'r') as f:
            text1 = f.read().decode('utf-8')
        with open(path2, 'r') as f:
            text2 = f.read().decode('utf-8')
    except:
        print(traceback.format_exc())
        raise
    finally:
        shutil.rmtree(tempdir)
    return text1, text2

def align(col_name, lang1, lang2, result_path, result_size, processes=1,
          restart=False, mode='old', method='yalign'):
    """Perform text aligning for articles

    :col_name: collection name
    :lang1: first language for aligning
    :lang2: second language for aligning
    :result_path: path for saving results
    :result_size: maximal size in symbols of result file
    :processes: number of processes for parallel processing
    :restart: restart aligner
    :mode: align algorithm to be used by yalign
    :returns: None

    """
    lang_id = '-'.join((lang1, lang2))
    model_name = '{}-{}'.format(lang1, lang2)
    if method == 'yalign':
        pool = Pool(processes, _init_model, [model_name, mode])
        align_fn = _align_text
    else:
        pool = Pool(processes)
        align_fn = _align_text_with_hunalign
    fs = FileStorage(lang1, lang2, result_path, result_size)
    col = pymongo.MongoClient().corpora[col_name]
    if restart:
        col.update({}, {'$unset': {'done_align': ''}}, multi=True)
    query = {
        'lang': lang1,
        'text': {'$exists': True},
        'done_align': {'$ne': lang_id}
    }
    i = col.find(query).count()
    log.info('Total articles to align: %s', i)
    log.info('Running %i threads for aligning', processes)
    for text_pair in pool.imap(align_fn, _iter_text(col, lang1, lang2)):
        if text_pair is not None:
            fs.put(*text_pair)
        i -= 1
        if i % 10 == 0:
            log.info('Left to align: %s', i)
