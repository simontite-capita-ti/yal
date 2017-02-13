# -*- coding: utf-8 -*-
"""
Description: Saves articles from db in plain text in parallel languages
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

def result_path(path, art_id, lang):
    name = '{}.{}'.format(art_id, lang)
    return os.path.join(path, name)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    log = logging.getLogger()
    parser = argparse.ArgumentParser(description='Saves articles from db in plain text in parallel languages')
    parser.add_argument('-l', '--languages', required=True, help='Comma separated list of languages to save, eg. en,pl,fr')
    parser.add_argument('-r', '--result', default='./', help='Path for saving article files')
    parser.add_argument('-o', '--source', required=True, help='Sorce of articles for saving: "wikipedia", "euronews"')
    args = parser.parse_args()
    args.result = os.path.expanduser(args.result)
    args.result = os.path.abspath(args.result)
    log.info('Saving articles to %s', args.result)
    langs = args.languages.split(',')
    get_art_path = partial(result_path, args.result)
    db = pymongo.MongoClient().corpora
    collection = db[args.source]
    query = {
        'text': {'$exists': True},
        'lang': langs[0]
    }
    count = 0
    for art in collection.find(query, no_cursor_timeout=True):
        arts_data = {
            langs[0]: art
        }
        for lang in langs[1:]:
            query = {
                'text': {'$exists': True},
                'lang': lang,
                'uid': art['uid']
            }
            related_art = collection.find_one(query)
            if not related_art:
                break
            arts_data[lang] = related_art
        else:
            for lang, art in arts_data.items():
                path = get_art_path(art['uid'], lang)
                with codecs.open(path, 'w', encoding='utf-8') as f:
                    f.write(remove_extra_spaces(art['text']))
        count += 1
        log.info('%i articles processed', count)
