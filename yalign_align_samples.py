# -*- coding: utf-8 -*-
"""
Description: Script for aligning articles in samples folder

Usage example:
    $ python yalign_align_samples.py --samples article_samples --lang1 pl --lang2 en --model pl-en --threshold 8.499999999999999e-07 --penalty 0.0149 -t 4
"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function


import logging
import os
from argparse import ArgumentParser, RawTextHelpFormatter
from multiprocessing import Pool, cpu_count
from pc.yalign import update_model
from pc.asyncalign import align_samples
from pc.fs import iter_samples

def align(args):
    """TODO: Docstring for align.

    :args: TODO
    :returns: TODO

    """
    align_samples(*args)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    log = logging.getLogger()
    parser = ArgumentParser(description=__doc__, formatter_class=RawTextHelpFormatter)
    parser.add_argument('-s', '--samples', required=True, help='Path to article samples')
    parser.add_argument('--lang1', required=True, help='Language 1')
    parser.add_argument('--lang2', required=True, help='Language 2')
    parser.add_argument('-m', '--model', required=True, help='Path to directory with yalign model')
    parser.add_argument('--threshold', type=float, required=True, help='Threshold value')
    parser.add_argument('--penalty', type=float, required=True, help='Penalty value')
    parser.add_argument('-t', '--threads', default=1, type=int, help='Number of threads to process information (default 1, 0 for auto)')
    args = parser.parse_args()
    if args.threads == 0:
        args.threads = cpu_count()
    log.info('Start')
    log.info('Updating model parameters')
    update_model(os.path.join(args.model, 'metadata.json'),
                 dict(threshold=args.threshold, penalty=args.penalty))
    pool = Pool(args.threads)
    align_args = ((args.model, args.lang1, args.lang2, art)
                   for art in iter_samples(args.samples))
    log.info('Aligning')
    import itertools
    for i, _ in enumerate(pool.imap_unordered(align, align_args)):
        log.info('%i articles processed', i + 1)
