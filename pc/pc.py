# -*- coding: utf-8 -*-
"""
"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

import os
import codecs
import logging
import traceback
from time import sleep
from threading import Thread
from Queue import Queue, Empty
from functools import partial
from uuid import uuid4
from glob import glob
import IPython
import pymongo
from collections import namedtuple
from IPython.config.loader import Config
from .dumpparser import parse_lang_links, parse_articles
from .WikiExtractor import clean
from .euronews import iter_all_articles, get_article_trans

LangLinkFile = namedtuple('LangLinkFile', ('lang', 'path'))
DumpFile = namedtuple('DumpFile', ('lang', 'path'))
log = logging.getLogger(__name__)
ip_cfg = Config()
ip_cfg.PromptManager.in_template = 'pp [\\#]:'
ip_cfg.InteractiveShell.confirm_exit = False

def _get_lang_link_files(path):
    for file_path in glob(os.path.join(path, '*.sql')):
        lang = os.path.basename(file_path)[:2]
        yield LangLinkFile(lang, file_path)

def _get_lang_links(path):
    for ll_file in _get_lang_link_files(path):
        with codecs.open(ll_file.path, encoding='utf-8', errors='replace') as f:
            for link in parse_lang_links(ll_file.lang, f):
                yield link

def _get_dump_files(path):
    for file_path in glob(os.path.join(path, '*.xml')):
        lang = os.path.basename(file_path)[:2]
        yield DumpFile(lang, file_path)

def extract_articles(dump_path, lang, debug=False):
    """Extracts articles from wiki dumps and stores to MongoDB

    :dump_path: path to dump files
    :lang: main language for extraction
    :debug: enable interactive shell on fail
    :returns: @todo

    """
    try:
        articles = {}
        uids = {}
        log.info('Starting')
        log.info('Extracting language links')
        i = 0
        for ll in _get_lang_links(dump_path):
            uid = uids.setdefault((ll.tgt_lang, ll.tgt_title), str(uuid4()))
            articles[(ll.orig_lang, ll.orig_id)] = uid
            i += 1
            if i % 100000 == 0:
                log.info('Articles count: %s', len(articles))

        log.info('Extracting article dumps')
        dumps = list(_get_dump_files(dump_path))
        main_dump = [d for d in dumps if d.lang == lang][0]
        dumps.remove(main_dump)
        db = pymongo.MongoClient().corpora
        log.info('Clearing current articles from db')
        db.articles.remove()
        db.articles.create_index('uid')
        db.articles.create_index('lang')
        db.articles.create_index('done_align')
        db.articles.create_index([('uid', pymongo.ASCENDING),
                                  ('lang', pymongo.ASCENDING)])

        log.info('Extracting articles for main language')
        arts_to_db = articles.copy()
        i = len(articles)
        for article in parse_articles(main_dump.lang, main_dump.path):
            try:
                uid = arts_to_db.pop((article.lang, article.id))
                text = clean(article.text)
            except Exception:
                pass
            else:
                db.articles.insert(dict(uid=uid, lang=article.lang,
                                        title=article.title,
                                        text=text))
                i -= 1
                if i % 100000 == 0:
                    log.info('Left to process: %s', int(len(arts_to_db)/2))
        log.info('Extracting articles for other languages (only if such article exists for main language)')
        for dump in dumps:
            log.info('Extrating articles from %s', dump.path)
            arts_to_db = articles.copy()
            i = len(articles)
            for article in parse_articles(dump.lang, dump.path):
                try:
                    uid = arts_to_db.pop((article.lang, article.id))
                except KeyError:
                    pass
                else:
                    if db.articles.find_one(dict(uid=uid)):
                        db.articles.insert(dict(uid=uid, lang=article.lang,
                                                title=article.title,
                                                text=clean(article.text)))
                    i -= 1
                    if i % 100000 == 0:
                        log.info('Left to process: %s', int(len(arts_to_db)/2))
        log.info('Done')
    except:
        log.error(traceback.format_exc())
        if debug:
            IPython.embed(config=ip_cfg, banner1='\nPP debugger\n\n')

def parse_euronews(start_url, langs, processes):
    """Parses euronews website and stores articles to DB

    :langs: article languages to extract
    :processes: number of processes for html extraction

    """
    lang_id = ','.join(langs)
    parse_queue = Queue(5)
    crawler_processes = max(1, int(processes * 0.4))
    parser_processes = max(1, int(processes * 0.6))
    log.info('Using %i crawler processes and %i parser processes',
             crawler_processes, parser_processes)
    db = pymongo.MongoClient().corpora
    db.articles.create_index('lang')
    db.articles.create_index('uid')
    db.articles.create_index('done')
    db.articles.create_index('done_align')
    db.articles.create_index([('uid', pymongo.ASCENDING),
                              ('lang', pymongo.ASCENDING)])
    db.articles.create_index([('lang', pymongo.ASCENDING),
                              ('done', pymongo.ASCENDING)])

    def _crawler():
        counter = 0
        for article in iter_all_articles(start_url, crawler_processes):
            query = dict(uid=article, lang='en')
            update = {'$set': query}
            db.euronews.update(query, update, upsert=True)
            counter += 1
            if counter % 1000 == 0:
                log.info('Total article links found: %i', counter)

    def _queue_arts():
        query = {
            'lang': 'en',
            '$or': [
                {'done': {'$exists': False}},
                {'done': {'$ne': lang_id}}
            ]
        }
        next_art = partial(db.euronews.find_one, query)
        counter = 0
        while True:
            article = next_art()
            if article is None and not crawler.is_alive():
                log.info('All articles send for parsing')
                break
            elif article:
                query = dict(uid=article['uid'], lang='en')
                update = {'$set': {'done': lang_id}}
                db.euronews.update(query, update, upsert=True)
                parse_queue.put(article)
                counter += 1
                if counter % 100 == 0:
                    log.info('Total articles sent for parsing: %i', counter)
            else:
                sleep(10)

    def _parser():
        while True:
            try:
                article = parse_queue.get(timeout=10)
            except Empty:
                if not crawler.is_alive():
                    break
            else:
                parse_queue.task_done()
                uid = article['uid']
                article_trans = get_article_trans(uid, langs)
                if article_trans:
                    for trans in article_trans:
                        query = dict(uid=uid, lang=trans.lang)
                        update = {'$set': dict(title=trans.title, text=trans.text)}
                        db.euronews.update(query, update, upsert=True)
    workers = []

    crawler = Thread(target=_crawler)
    crawler.daemon = True
    crawler.start()
    workers.append(crawler)

    arts_queuer = Thread(target=_queue_arts)
    arts_queuer.daemon = True
    arts_queuer.start()
    workers.append(arts_queuer)

    for _ in range(parser_processes):
        parser = Thread(target=_parser)
        parser.daemon = True
        parser.start()
        workers.append(parser)

    while True:
        for w in workers:
            w.join(1)
        if all([not w.is_alive() for w in workers]):
            break
