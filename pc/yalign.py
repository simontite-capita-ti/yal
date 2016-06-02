# -*- coding: utf-8 -*-
"""
Description: 
"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

import json

def update_model(path, model):
    """@todo: Docstring for update_model.

    :path: @todo
    :model: @todo
    :returns: @todo

    """
    with open(path) as f:
        current_model = json.load(f)
    current_model.update(model)
    with open(path, 'w') as f:
        json.dump(current_model, f)
