# -*- coding: utf-8 -*-
"""
Description: Trying random parameters for model of yalign selects best
parameters for aligning provided text samples
"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

import logging
from argparse import ArgumentParser
from pc.yalignselection import YSelection
from multiprocessing import cpu_count

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    log = logging.getLogger()
    parser = ArgumentParser(description='Trying random parameters for model of yalign selects best parameters for aligning provided text samples')
    parser.add_argument('-s', '--samples', required=True, help='Path to article samples')
    parser.add_argument('--lang1', required=True, help='Language 1')
    parser.add_argument('--lang2', required=True, help='Language 2')
    parser.add_argument('-m', '--model', required=True, help='Path to directory with yalign model')
    parser.add_argument('--threshold', type=float, required=True, help='Threshold value')
    parser.add_argument('--threshold_step', type=float, required=True, help='Threshold change step')
    parser.add_argument('--threshold_step_count', type=int, required=True, help='Number of steps to check around threshold value')
    parser.add_argument('--penalty', type=float, required=True, help='Penalty value')
    parser.add_argument('--penalty_step', type=float, required=True, help='Penalty change step')
    parser.add_argument('--penalty_step_count', type=int, required=True, help='Number of steps to check around penalty value')
    parser.add_argument('-r', '--result', default='yalign_selection.csv', help='Path to csv file for saving selection results')
    parser.add_argument('--length', default=0.9, type=float, help='Length filter for sentences (min 0, max 1)')
    parser.add_argument('--similarity', default=0.9, type=float, help='Similarity filter for sentences (min 0, max 1)')
    parser.add_argument('-t', '--threads', default=0, type=int, help='Number of threads to process information (default 0 - auto)')
    args = parser.parse_args()
    if args.threads == 0:
        args.threads = cpu_count()
    log.info('Start')
    selection_conf = dict(
        threshold=dict(start=args.threshold, step=args.threshold_step, count=args.threshold_step_count),
        penalty=dict(start=args.penalty, step=args.penalty_step, count=args.penalty_step_count))
    ys = YSelection(args.lang1, args.lang2, args.samples, args.model,
                    selection_conf, args.result, args.length, args.similarity,
                    processes=args.threads)
    ys.run()
    log.info('Done')
