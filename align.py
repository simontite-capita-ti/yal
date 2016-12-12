# -*- coding: utf-8 -*-
"""
Description: Aligning text of articles stored in MongoDB
"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

import argparse
import logging
from multiprocessing import cpu_count
from pc.align import align

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Aligning text using yaling')
    parser.add_argument('-l', '--language', required=True, help='Language pair to be aligned (eg. en-pl)')
    parser.add_argument('-r', '--result', default='./', help='Path for saving result files')
    parser.add_argument('-s', '--size', type=int, default=50000000, help='Maximal allowed size of file')
    parser.add_argument('-v', action='store_true', help='Verbose mode')
    parser.add_argument('-t', '--threads', type=int, default=0, help='Number of threads for text aligning, should be less or equal to number of CPU cores, 0 for autodetection (by default)')
    parser.add_argument('-o', '--source', required=True, help='Sorce of articles for aligning: "wikipedia", "euronews"')
    parser.add_argument('--restart', action='store_true', help='Restart aligner')
    parser.add_argument('-m', '--mode', help='Alignment mode to be used by yalign')
    parser.add_argument('--hunalign', action='store_true', help='Align using hunalign')
    args = parser.parse_args()
    if args.v:
        logging.basicConfig(level=logging.INFO)
    if args.threads == 0:
        args.threads = cpu_count()
    lang1, lang2 = args.language.split('-')
    method = 'yalign'
    if args.hunalign:
        method = 'hunalign'
    align(
        args.source,
        lang1,
        lang2,
        args.result,
        args.size,
        processes=args.threads,
        restart=args.restart,
        mode=args.mode,
        method=method
    )
