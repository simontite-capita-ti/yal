# -*- coding: utf-8 -*-
"""
Description: Selects random articles pairs and saves to disk
"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

import logging
from argparse import ArgumentParser
from pc.artsampling import extract_samples

if __name__ == '__main__':
    parser = ArgumentParser(
        description='Selects random articles pairs and saves to disk')
    parser.add_argument('-o', '--source', default='wikipedia', type=str,
                        help='Article source for selection (wikipedia/euronews)')
    parser.add_argument('-c', '--count', default=100, type=int,
                        help='Number of articles to select')
    parser.add_argument('-p', '--path', default='./article_samples', type=str,
                        help='Path for saving article samples')
    parser.add_argument('-l', '--languages', required=True,
                        help='Language pair for sampling (eg. en-pl)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Verbose mode')

    args = parser.parse_args()

    if args.source == 'wikipedia':
        args.source = 'articles'
    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.ERROR)

    log = logging.getLogger()

    langs = args.languages.split('-')[:2]
    log.info('Start')
    extract_samples(args.path, args.source, args.count, langs)
    log.info('Done')
