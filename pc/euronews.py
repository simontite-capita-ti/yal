# -*- coding: utf-8 -*-
"""
Description: Euronews parsing data and functions
"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

import logging
from multiprocessing import Pool
from itertools import chain
from .http import get_html
from lxml import html as html_parser
from .model import Article

root_url = 'http://euronews.com'
xp_year_list = '//div[@id="main-content"]//h2[contains(@class, "archiveDateList")]/a/@href'
xp_day_list = '//div[@id="main-content"]//td[contains(@class, "usedDay")]/a/@href'
xp_article_list = '//div[@id="main-content"]//ul[contains(@class, "article-list")]//a/@href'
xp_article_title = '//div[@id="main-content"]//div[@id="title-wrap-new"]/h1/a/text()'
xp_article_text_node = '//div[@id="main-content"]//div[@id="article-text"]'

# Attributes:
# lang - language
# value - url to article
xp_article_lang_nodes = '//div[@id="languageSelection"]//option'

log = logging.getLogger(__name__)

def full_url(link):
    """@todo: Docstring for full_url.

    :link: @todo
    :returns: @todo

    """
    if link.startswith('/'):
        return root_url + link
    else:
        return link

def iter_years(url):
    """@todo: Docstring for iter_years.

    :url: @todo
    :returns: @todo

    """
    log.debug('Year url %s', url)
    html = get_html(url)
    if html is None:
        return
    e = html_parser.document_fromstring(html)
    for year in e.xpath(xp_year_list):
        log.debug('Year %s', year)
        yield full_url(year)

def iter_days(years):
    """@todo: Docstring for iter_days.

    :years: @todo
    :returns: @todo

    """
    for year in years:
        log.debug('Days for year %s', year)
        html = get_html(year)
        if html is None:
            continue
        e = html_parser.document_fromstring(html)
        for day in e.xpath(xp_day_list):
            log.debug('Day %s', day)
            yield full_url(day)

def get_day_articles(day):
    """@todo: Docstring for get_day_articles.

    :day: @todo
    :returns: @todo

    """
    log.debug('Articles for day %s', day)
    html = get_html(day)
    if html is None:
        return []
    e = html_parser.document_fromstring(html)
    articles = e.xpath(xp_article_list)
    return [full_url(a) for a in articles]

def iter_articles(days, processes=1):
    """@todo: Docstring for iter_articles.

    :days: @todo
    :returns: @todo

    """
    pool = Pool(processes)
    articles = chain.from_iterable(pool.imap(get_day_articles, days))
    for article in articles:
        log.debug('Article %s', article)
        yield full_url(article)

def iter_all_articles(url, processes=1):
    """@todo: Docstring for iter_all_articles.

    :url: @todo
    :returns: @todo

    """
    years = iter_years(url)
    days = iter_days(years)
    articles = iter_articles(days, processes)
    for article in articles:
        yield article

def get_article(lang, art_id, html):
    e = html_parser.document_fromstring(html)
    try:
        title = e.xpath(xp_article_title)[0]
        text = e.xpath(xp_article_text_node)[0]
        for script in text.xpath('//script'):
            script.getparent().remove(script)
        text = text.text_content()
        return Article(lang, art_id, title, text)
    except (IndexError, UnicodeDecodeError):
        return None

def get_article_trans(url, langs=None):
    """@todo: Docstring for get_article_trans.

    :url: @todo
    :langs: list of languages to extract for give article, None - for all
        available
    :returns: @todo

    """
    def _need_lang(lang):
        return langs is None or lang in langs

    def _trans(html):
        e = html_parser.document_fromstring(html)
        trans = []
        for option in e.xpath(xp_article_lang_nodes):
            lang = option.get('lang')
            art_url = full_url(option.get('value'))
            if lang != 'en' and lang and art_url and _need_lang(lang):
                trans.append((lang, art_url))
        return trans

    log.debug('Getting articles translations for %s', url)
    html = get_html(url)
    if html is None:
        return None
    articles = []
    if _need_lang('en'):
        log.debug('Translation en')
        articles.append(get_article('en', url, html))
    for lang, art_url in _trans(html):
        log.debug('Translation %s, at %s', lang, art_url)
        html = get_html(art_url)
        if html is None:
            continue
        articles.append(get_article(lang, url, html))
    articles = [a for a in articles if a is not None]
    if langs:
        have_langs = set([a.lang for a in articles])
        if have_langs != set(langs):
            return None
    return articles
