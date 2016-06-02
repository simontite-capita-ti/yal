# -*- coding: utf-8 -*-
"""
Description: 
"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

import logging
import csv
from multiprocessing import Pool
from collections import namedtuple
from itertools import product
from .fs import iter_samples
from .asyncsim import get_sim_compact

ModelParams = namedtuple('ModelParams', ('threshold', 'penalty'))

def iter_num(n, step, step_count):
    start = n - step * step_count
    for i in xrange(step_count*2+1):
        yield start + i * step

class YSelection(object):

    """Docstring for YSelection. """

    def __init__(self, lang1, lang2, samples_path, model_path, selection_conf,
                 result_path, len_flt, sim_flt, processes=1):
        """@todo: to be defined1.

        :samples_path: @todo
        :result_path: @todo
        :len_flt: @todo
        :sim_flt: @todo

        """
        self.lang1 = lang1
        self.lang2 = lang2
        self.samples_path = samples_path
        self.model_path = model_path
        self.selection_conf = selection_conf
        self.result_path = result_path
        self.len_flt = len_flt
        self.sim_flt = sim_flt

        self.pool = Pool(processes)
        self.log = logging.getLogger(__name__)
        self.log.info('Using %i threads', processes)

    def _iter_params(self):
        """@todo: Docstring for _iter_params.
        :returns: @todo

        """
        iter_threshold = iter_num(self.selection_conf['threshold']['start'],
                                  self.selection_conf['threshold']['step'],
                                  self.selection_conf['threshold']['count'])
        iter_penalty = iter_num(self.selection_conf['penalty']['start'],
                                self.selection_conf['penalty']['step'],
                                self.selection_conf['penalty']['count'])
        for threshold, penalty in product(iter_threshold, iter_penalty):
            yield ModelParams(threshold, penalty)

    def _iter_sim_param(self):
        """@todo: Docstring for _iter_sim_param.
        :returns: @todo

        """
        for param in self._iter_params():
            yield (self.lang1, self.lang2, self.samples_path, param.threshold,
                   param.penalty, self.model_path, self.len_flt, self.sim_flt)

    def run(self):
        """@todo: Docstring for run.
        :returns: @todo

        """
        csv_writer = csv.writer(open(self.result_path, 'a'))
        for th, pen, sim in self.pool.imap(get_sim_compact, self._iter_sim_param()):
            self.log.info('Similarity for %s is %f', (th, pen), sim)
            csv_writer.writerow((th, pen, sim))
