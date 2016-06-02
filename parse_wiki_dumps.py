# -*- coding: utf-8 -*-
"""
Description: Parsing of media wiki dump files and storing articles to MongoDB
"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

import argparse
import logging
from pc.pc import extract_articles

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parsing of media wiki dump files and storing articles to MongoDB')
    parser.add_argument('-d', '--dump', required=True, help='Path to wiki dumps')
    parser.add_argument('-l', '--mainlang', required=True, help='Main language (only articles and language pairs available for this language is processed)')
    parser.add_argument('-v', action='store_true', help='Verbose mode')
    parser.add_argument('--debug', action='store_true', help='Debug mode')
    args = parser.parse_args()
    if args.v:
        logging.basicConfig(level=logging.INFO)
    extract_articles(args.dump, args.mainlang, debug=args.debug)
