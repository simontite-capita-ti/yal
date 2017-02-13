# -*- coding: utf-8 -*-
'''
File: pool.py
Author: rsk <rskbox@gmail.com>
Description: Implementation of LightDB class, which allows to connect to sqlite
db and run transcations easy
'''

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import sqlite3
import logging
import functools
import time
import random

log = logging.getLogger(__name__)

class LightDB(object):

    """Docstring for LightDB. """

    def __init__(self, db_path):
        """@todo: to be defined1.

        :db_path: @todo

        """
        self.db_path = db_path

    def __repr__(self):
        """@todo: Docstring for __repr__.
        :returns: @todo

        """
        return '<LightDB %s>' % self.db_path

    def _run_transaction(self, operation):
        """@todo: Docstring for _run_transaction.

        :operation: @todo
        :returns: @todo

        """
        data = None

        try:
            con = sqlite3.connect(self.db_path)
        except sqlite3.Error as e:
            log.error('Can\'t open connection to database "%s": %s', self.db_path, e)
            return None

        con.row_factory = sqlite3.Row
        try:
            cursor = con.cursor()
            while True:
                try:
                    cursor.execute('begin immediate')
                except sqlite3.OperationalError as e:
                    log.warn('Can\'t start transaction for db "%s", waiting and trying again: %s',
                             self.db_path, e)
                    time.sleep(random.uniform(0, 10))
                else:
                    # transaction started
                    break
            try:
                data = operation(cursor)
                con.commit()
            except sqlite3.Error as e:
                con.rollback()
                raise e

        except sqlite3.Error as e:
            log.error('Can\'t run operation for db "%s": %s', self.db_path, e)
        finally:
            cursor.close()
            con.close()

        return data

    def _run(self, operation):
        """@todo: Docstring for _run.

        :operation: @todo
        :returns: @todo

        """
        data = None

        try:
            con = sqlite3.connect(self.db_path)
        except sqlite3.Error as e:
            log.error('Can\'t open connection to database "%s": %s', self.db_path, e)
            return None

        con.row_factory = sqlite3.Row
        try:
            cursor = con.cursor()

            try:
                data = operation(cursor)
                con.commit()
            except sqlite3.Error as e:
                con.rollback()
                raise e

        except sqlite3.Error as e:
            log.error('Can\'t run operation for db "%s": %s', self.db_path, e)
        finally:
            cursor.close()
            con.close()

        return data
