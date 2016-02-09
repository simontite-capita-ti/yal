# -*- coding: utf-8 -*-
"""
"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

import codecs
import os

class FileStorage(object):

    """FileStorage allows store text corpora in parallel files"""

    def __init__(self, id1, id2, path, max_size):
        """
        :id1: prefix for first file
        :id2: prifix for second file
        :path: path for storing files
        :max_size: maximal file size in symbols

        """
        self.id1 = id1
        self.id2 = id2
        self.path = path
        self.max_size = max_size

        self.file1 = None
        self.file2 = None
        self.written = 0
        self.counter = 0
        self.next_files()

    def next_files(self):
        """@todo: Docstring for next_files.

        :returns: @todo

        """
        if self.file1:
            self.file1.close()
        if self.file2:
            self.file2.close()
        path1 = os.path.join(self.path, '{}-{}.txt'.format(self.id1, self.counter))
        path2 = os.path.join(self.path, '{}-{}.txt'.format(self.id2, self.counter))
        self.file1 = codecs.open(path1, 'a', encoding='utf-8')
        self.file2 = codecs.open(path2, 'a', encoding='utf-8')
        self.written = 0
        self.counter += 1

    def put(self, text1, text2):
        """@todo: Docstring for put.

        :text1: @todo
        :text2: @todo
        :returns: @todo

        """
        if isinstance(text1, str):
            text1 = text1.decode('utf-8', errors='ignore')
        if isinstance(text2, str):
            text2 = text2.decode('utf-8', errors='ignore')
        self.file1.write(text1)
        self.file2.write(text2)
        self.written += len(text1)
        if self.written > self.max_size:
            self.next_files()
