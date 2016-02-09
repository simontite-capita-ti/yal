# -*- coding: utf-8 -*-
"""
Description: 
"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

import logging
import os
import gc
from yalign import YalignModel, text_to_document
from .text import remove_extra_spaces

log = logging.getLogger()

def align_samples(model, lang1, lang2, art):
    """TODO: Docstring for align_samples.

    :model: TODO
    :lang1: TODO
    :lang2: TODO
    :art: TODO
    :returns: TODO

    """
    model = YalignModel.load(model)
    try:
        doc1 = text_to_document(remove_extra_spaces(art['orig'][lang1]))
        doc2 = text_to_document(remove_extra_spaces(art['orig'][lang2]))
        pairs = model.align(doc1, doc2)
    except:
        log.error('Error aligning %s', art['path'])
    else:
        # to_text returns <str>
        pairs = [(p1.to_text(), p2.to_text()) for p1, p2 in pairs]
        text1 = ''.join(p[0] + '\n' for p in pairs)
        text2 = ''.join(p[1] + '\n' for p in pairs)
        path1 = os.path.join(art['path'], '{}_yalign'.format(lang1))
        path2 = os.path.join(art['path'], '{}_yalign'.format(lang2))
        with open(path1, 'w') as f:
            f.write(text1)
        with open(path2, 'w') as f:
            f.write(text2)
    finally:
        del model
        gc.collect()
