# -*- coding: utf-8 -*-
"""
Description: Parsing of mediawiki dump files
"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

import re
from collections import namedtuple
from lxml import etree
from .model import Article

LangLink = namedtuple('LangLink', ('orig_lang', 'orig_id', 'tgt_lang', 'tgt_title'))
lang_link_re = re.compile(u"\(([0-9]+),'([^']+)','([^']+)'\)")

WIKI_NS = {'w': 'http://www.mediawiki.org/xml/export-0.10/'}
PAGE_TAG = '{http://www.mediawiki.org/xml/export-0.10/}page'

def parse_lang_links(orig_lang, file):
    """Parses sql dump of language links

    :orig_lang: name of main language (for which language links is created)
    :file: file with data
    :returns: tuple (main lang, article id, target lang, target title)

    """
    data = ''
    while True:
        data += file.read(16000)
        if not data:
            break
        for match in lang_link_re.finditer(data):
            if ':' not in match.group(3):
                link = LangLink(orig_lang, int(match.group(1)), match.group(2),
                                match.group(3))
                yield link
        try:
            data = data[data.rindex(u')')+1:]
        except ValueError:
            data = ''

def parse_articles(lang, path):
    """Parses wikimedia xml article pages dump

    :lang: language of dump
    :path: path to file
    :returns: tuple (lang, id, title, text)

    """
    with open(path) as f:
        assert WIKI_NS['w'] in next(f), 'Incorrect version of media wikidump'
    for _, elem in etree.iterparse(path, tag=PAGE_TAG):
        article_id = int(elem.find('./w:id', namespaces=WIKI_NS).text)
        title = elem.find('./w:title', namespaces=WIKI_NS).text
        text = elem.find('./w:revision/w:text', namespaces=WIKI_NS).text
        elem.clear()
        article = Article(lang, article_id, title, text)
        yield article
