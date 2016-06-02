# -*- coding: utf-8 -*-
"""
Description: 
"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

import os
import json
import gc
from multiprocessing import Lock
from yalign import YalignModel, text_to_document
from .fs import iter_samples
from .text import remove_extra_spaces, line_sim
from .yalign import update_model

model_lock = Lock()

def get_sim_compact(args):
    sim = get_similarity(*args)
    return args[3], args[4], sim

def get_similarity(lang1, lang2, sample_path, threshold, penalty, model,
                   len_flt, sim_flt):
    """@todo: Docstring for get_similarity.

    :sample_path: @todo
    :threshold: @todo
    :penalty: @todo
    :model: @todo
    :returns: @todo

    """
    with model_lock:
        model_conf_path = os.path.join(model, 'metadata.json')
        update_model(model_conf_path, dict(threshold=threshold, penalty=penalty))
        model = YalignModel.load(model)
    similarity = []
    for sample in iter_samples(sample_path):
        try:
            doc1 = text_to_document(remove_extra_spaces(sample['orig'][lang1]))
            doc2 = text_to_document(remove_extra_spaces(sample['orig'][lang2]))
            pairs = model.align(doc1, doc2)
        except:
            similarity.append(0)
        else:
            pairs = [(p[0].to_text(), p[1].to_text()) for p in pairs]
            text1 = [p[0] for p in pairs]
            text1 = [t+'\n' for t in text1]
            text1 = ''.join(text1)
            text2 = [p[1] for p in pairs]
            text2 = [t+'\n' for t in text2]
            text2 = ''.join(text2)
            try:
                text2 = text2.decode('utf-8')
            except UnicodeEncodeError:
                del model
                gc.collect()
                return 0
            similarity.append(line_sim(text2, sample['human'][lang2], len_flt, sim_flt))
    del model
    gc.collect()
    return sum(similarity)/len(similarity)
