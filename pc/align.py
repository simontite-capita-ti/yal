# -*- coding: utf-8 -*-
"""
Description: Text aligning
"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

import logging
import pymongo
from multiprocessing import Pool
from yalign import YalignModel
from yalign import text_to_document
from .filestorage import FileStorage
from .text import remove_extra_spaces

log = logging.getLogger(__name__)
model = None

def _init_model(model_name, mode):
    """@todo: Docstring for _init_model.

    :model_name: @todo
    :returns: @todo

    """
    global model
    model = YalignModel.load(model_name)
    model.mode = mode

def _iter_text(db, lang1, lang2):
    lang_id = '-'.join((lang1, lang2))
    query = {
        'lang': lang1,
        'done_align': {'$ne': lang_id}
    }
    for art1 in db.articles.find(query, timeout=False):
        query = {'uid': art1['uid'], 'lang': lang1}
        update = {'$set': {'done_align': lang_id}}
        db.articles.update(query, update)
        art2 = db.articles.find_one(dict(uid=art1['uid'], lang=lang2))
        if not art2:
            continue
        yield (art1, art2)

def _iter_euronews(db, lang1, lang2):
    lang_id = '-'.join((lang1, lang2))
    query = {
        'lang': lang1,
        'text': {'$exists': True},
        'done_align': {'$ne': lang_id}
    }
    for art1 in db.euronews.find(query, timeout=False):
        query = {'uid': art1['uid'], 'lang': lang1}
        update = {'$set': {'done_align': lang_id}}
        db.euronews.update(query, update)
        art2 = db.euronews.find_one(dict(uid=art1['uid'], lang=lang2))
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

def align(lang1, lang2, result_path, result_size, processes=1, restart=False,
          mode='old'):
    """Perform text aligning for articles

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
    pool = Pool(processes, _init_model, [model_name, mode])
    fs = FileStorage(lang1, lang2, result_path, result_size)
    db = pymongo.MongoClient().corpora
    if restart:
        db.articles.update({}, {'$unset': {'done_align': ''}}, multi=True)
    query = {
        'lang': lang1,
        'done_align': {'$ne': lang_id}
    }
    i = db.articles.find(query).count()
    log.info('Total articles to align: %s', i)
    log.info('Running %i threads for aligning', processes)
    for text_pair in pool.imap(_align_text, _iter_text(db, lang1, lang2)):
        if text_pair is not None:
            fs.put(*text_pair)
        i -= 1
        if i % 10 == 0:
            log.info('Left to align: %s', i)

def align_euronews(lang1, lang2, result_path, result_size, processes=1, restart=False,
                   mode='old'):
    """Perform text aligning for articles from euronews

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
    pool = Pool(processes, _init_model, [model_name, mode])
    fs = FileStorage(lang1, lang2, result_path, result_size)
    db = pymongo.MongoClient().corpora
    if restart:
        db.euronews.update({}, {'$unset': {'done_align': ''}}, multi=True)
    query = {
        'lang': lang1,
        'text': {'$exists': True},
        'done_align': {'$ne': lang_id}
    }
    i = db.euronews.find(query).count()
    log.info('Total articles to align: %s', i)
    log.info('Running %i threads for aligning', processes)
    for text_pair in pool.imap(_align_text, _iter_euronews(db, lang1, lang2)):
        if text_pair is not None:
            fs.put(*text_pair)
        i -= 1
        if i % 10 == 0:
            log.info('Left to align: %s', i)
