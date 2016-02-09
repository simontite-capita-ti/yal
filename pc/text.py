# -*- coding: utf-8 -*-
"""
Description: Functions for manipulating text
"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

import re
from difflib import SequenceMatcher

re_win_newline = re.compile(u'\r\n', re.MULTILINE)
re_newline = re.compile(u'\r\n|\n', re.MULTILINE)
re_extra_space = re.compile(ur'\s{2,}')

def get_clean_tokens(tokens):
    """@todo: Docstring for get_clean_tokens.

    :tokens: @todo
    :returns: @todo

    """
    tokens = [t.strip() for t in tokens]
    tokens = [t for t in tokens if t]
    return tokens

def remove_extra_spaces(text):
    """@todo: Docstring for remove_extra_spaces.

    :text: @todo
    :returns: @todo

    """
    text = re_win_newline.sub(u'\n', text)
    text = (t for t in text.split(u'\n'))
    text = (t.strip() for t in text)
    text = (re_extra_space.sub(' ', t) for t in text)
    text = (t for t in text if len(t) >= 2)
    return '\n'.join(text)

def similarity(text1, text2):
    """@todo: Docstring for similarity.

    :text1: @todo
    :text2: @todo
    :returns: @todo

    """
    m = SequenceMatcher(a=text1, b=text2)
    return m.ratio()

def is_similar(text1, text2, len_flt=0.9, sim_flt=0.9):
    """@todo: Docstring for is_similar.

    :text1: @todo
    :text2: @todo
    :returns: @todo

    """
    len_diff = min(len(text1), len(text2))/max(len(text1), len(text2))
    if len_diff < len_flt:
        return False
    if similarity(text1, text2) < sim_flt:
        return False
    return True

def line_sim(text1, text2, len_flt, sim_flt):
    """Similarity between lines in text files

    :text1: @todo
    :text2: @todo
    :len_flt: @todo
    :sim_flt: @todo
    :returns: @todo

    """
    text1 = get_clean_tokens(re_newline.split(text1))
    text2 = get_clean_tokens(re_newline.split(text2))
    sim_count = 0
    for sent1 in text1:
        for sent2 in text2:
            if is_similar(sent1, sent2, len_flt, sim_flt):
                sim_count += 1
                break
    if len(text1) > 0:
        return sim_count/len(text1)
    else:
        return 0
