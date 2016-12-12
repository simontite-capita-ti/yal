# -*- coding: utf-8 -*-
"""
Description: Cleans mongo DB from all data used for parallel_corpora
"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

import pymongo

if __name__ == '__main__':
    db = pymongo.MongoClient()
    if raw_input('Type [yes] to confirm full DB cleanup: ') == 'yes':
        print('Cleaning DB...')
        db.drop_database('corpora')
        print('Done')
    else:
        print('Canceled')
