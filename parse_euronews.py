# -*- coding: utf-8 -*-
"""
Description: Crawles euronews website and extracts article texts
"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

import argparse
import logging
from pc.pc import parse_euronews
from conf import conf

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Crawler for euronews website')
    parser.add_argument('-l', '--langs', required=True, help='Comma separated list of languages to extract, eg. "en,pl"')
    parser.add_argument('-v', action='store_true', help='Verbose mode')
    parser.add_argument('-t', '--threads', type=int, default=5, help='Number of threads for crawler')
    args = parser.parse_args()
    if args.v:
        logging.basicConfig(level=logging.INFO)
        logging.getLogger('urllib3').setLevel(logging.ERROR)
    parse_euronews(conf.euronews_start_url, args.langs.split(','), args.threads)
