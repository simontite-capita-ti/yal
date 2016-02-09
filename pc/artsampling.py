# -*- coding: utf-8 -*-
"""
"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

import logging
import random
import os
from codecs import open as copen
from pymongo import MongoClient
from werkzeug.utils import secure_filename
from .text import remove_extra_spaces

log = logging.getLogger()

def save_sample(path, art1, art2):
    """@todo: Docstring for save_sample.

    :path: @todo
    :art1: @todo
    :art2: @todo
    :returns: @todo

    """
    path = os.path.join(path, secure_filename(art1['uid']))
    try:
        os.makedirs(path)
    except os.error:
        pass
    for art in [art1, art2]:
        with copen(os.path.join(path, art['lang']), 'w', encoding='utf-8') as f:
            f.write(remove_extra_spaces(art['text']))
        with copen(os.path.join(path, art['lang']+'_orig'), 'w', encoding='utf-8') as f:
            f.write(remove_extra_spaces(art['text']))

def extract_samples(path, source, count, langs):
    """@todo: Docstring for extract_samples.

    :path: @todo
    :source: @todo
    :count: @todo
    :langs: @todo
    :returns: @todo

    """
    db = getattr(MongoClient().corpora, source)
    art_ids = []
    query = {'lang': langs[0], 'text': {'$exists': True}}
    log.info('Preparing list of articles')
    for art in db.find(query, timeout=False):
        art_ids.append(art['uid'])
    random.shuffle(art_ids)
    samples = []
    log.info('Searching for pairs')
    for uid in art_ids:
        query = {'uid': uid, 'lang': langs[1], 'text': {'$exists': True}}
        art2 = db.find_one(query)
        if not art2:
            continue
        query = {'uid': uid, 'lang': langs[0]}
        art1 = db.find_one(query)
        samples.append((art1, art2))
        if len(samples) == count:
            break
    log.info('Saving samples')
    for art1, art2 in samples:
        save_sample(path, art1, art2)
