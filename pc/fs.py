# -*- coding: utf-8 -*-
"""
Description: Functions for working with filesystem
"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

import os
from codecs import open as copen

def read_file(path):
    """@todo: Docstring for read_file.

    :path: @todo
    :returns: @todo

    """
    with copen(path, encoding='utf-8', errors='replace') as f:
        return f.read()

def iter_samples(path):
    """@todo: Docstring for iter_samples.

    :path: @todo
    :returns: @todo

    """
    human = {}
    orig = {}
    for sample_path in os.listdir(path):
        sample_path = os.path.join(path, sample_path)
        for art in os.listdir(sample_path):
            art_path = os.path.join(sample_path, art)
            if '_orig' in art:
                orig[art[:2]] = read_file(art_path)
            elif len(art) == 2:
                human[art] = read_file(art_path)
        yield dict(orig=orig, human=human, path=sample_path)
