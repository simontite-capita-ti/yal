# -*- coding: utf-8 -*-
"""
Description: Saves articles from db in plain text
"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

import argparse
import os
import logging
import codecs
from functools import partial
import pymongo
from werkzeug.utils import secure_filename
from pc.text import remove_extra_spaces

def result_path(path, lang):
    """@todo: Docstring for result_path.

    :path: @todo
    :lang: @todo
    :returns: @todo

    """
    return os.path.join(path, lang)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    log = logging.getLogger()
    parser = argparse.ArgumentParser(description='Saves articles from db in plain text')
    parser.add_argument('-l', '--languages', required=True, help='Comma separated list of languages to save, eg. en,pl,fr')
    parser.add_argument('-r', '--result', default='./', help='Path for saving article files')
    parser.add_argument('-o', '--source', required=True, help='Sorce of articles for saving: "wikipedia", "euronews"')
    args = parser.parse_args()
    args.result = os.path.expanduser(args.result)
    args.result = os.path.abspath(args.result)
    log.info('Saving articles to %s', args.result)
    langs = args.languages.split(',')
    lang_path = partial(result_path, args.result)
    for lang in langs:
        if not os.path.exists(lang_path(lang)):
            os.makedirs(lang_path(lang))
    db = pymongo.MongoClient().corpora
    collection = db[args.source]
    query = {'text': {'$exists': True}}
    count = 0
    for lang in langs:
        query['lang'] = lang
        for art in collection.find(query, no_cursor_timeout=True):
            path = os.path.join(lang_path(lang), secure_filename(art['uid']))
            with codecs.open(path, 'w', encoding='utf-8') as f:
                f.write(remove_extra_spaces(art['text']))
            count += 1
            if count % 1000 == 0:
                log.info('%i articles saved', count)
