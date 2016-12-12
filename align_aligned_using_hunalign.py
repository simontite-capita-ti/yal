# -*- coding: utf-8 -*-
"""
Description: 
"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

import os
import subprocess
import tempfile
import logging
from argparse import ArgumentParser

_readme = """
"""
_readme = _readme.strip()

logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
log = logging.getLogger('alignalign')

hunalign_bin = os.path.join(os.path.dirname(__file__), 'pc', 'hunalign')

def get_conf():
    parser = ArgumentParser(description='Aligns texts from aligned result, using hunalign', usage=_readme)
    parser.add_argument('source', help='Path to aligned results')
    parser.add_argument('target', help='Path to realigned results')
    return parser.parse_args()

def align(path1, path2):
    """TODO: Docstring for align.

    :art_pair: TODO
    :returns: TODO

    """
    result = subprocess.check_output([
        hunalign_bin,
        '-text',
        '-utf',
        '/dev/null',
        path1,
        path2
    ])
    sentences = []
    result = result.decode('utf-8')
    for rec in result.split('\n'):
        tokens = rec.split('\t')
        if len(tokens) == 3:
            sentences.append((tokens[0], tokens[1]))
    # no need to save empty file
    if not sentences:
        return None
    # filter and strip
    sentences = [
        (s1.strip(u'\t\n\r\f\v \ufeff'),
            s2.strip(u'\t\n\r\f\v \ufeff'))
        for s1, s2 in sentences
    ]
    sentences = [(s1, s2) for s1, s2 in sentences
                    if s1 and s2 and not s1 == s2]
    text1 = u'\n'.join(s1 for s1, _ in sentences)
    text2 = u'\n'.join(s2 for _, s2 in sentences)
    return text1, text2

def parts_align(path1, path2):
    """TODO: Docstring for parts_align.

    :path1: TODO
    :path2: TODO
    :returns: TODO

    """
    text1 = ''
    text2 = ''
    with open(path1) as f1, open(path2) as f2:
        fd1, temp_path1 = tempfile.mkstemp()
        fd2, temp_path2 = tempfile.mkstemp()
        with open(temp_path1, 'w', 0) as tf1, open(temp_path2, 'w', 0) as tf2:
            size1 = 0
            size2 = 0
            for rec1, rec2 in zip(f1, f2):
                size1 += len(rec1)
                size2 += len(rec2)
                tf1.write(rec1)
                tf2.write(rec2)
                if size1 > 1048576 or size2 > 1048576:
                    next_text1, next_text2 = align(temp_path1, temp_path2)
                    text1 += next_text1
                    text2 += next_text2
                    size1 = size2 = 0
                    tf1.seek(0)
                    tf1.truncate()
                    tf2.seek(0)
                    tf2.truncate()
            if size1 and size2:
                next_text1, next_text2 = align(temp_path1, temp_path2)
                text1 += next_text1
                text2 += next_text2
        os.close(fd1)
        os.close(fd2)
        os.unlink(temp_path1)
        os.unlink(temp_path2)
    return text1, text2

def get_pairs(path):
    """TODO: Docstring for get_pairs.

    :path: TODO
    :returns: TODO

    """
    pairs = {}
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            pair_id = filename.split('-', 1)[1]
            pairs.setdefault(pair_id, [])
            pairs[pair_id].append(file_path)
            if len(pairs[pair_id]) == 2:
                yield pairs[pair_id]

def main():
    conf = get_conf()
    try:
        os.makedirs(conf.target)
    except os.error:
        pass
    for i, (path1, path2) in enumerate(get_pairs(conf.source)):
        log.info('Processing pair %i', i)
        result = parts_align(path1, path2)
        if result:
            text1, text2 = result
            name1 = os.path.basename(path1)
            name2 = os.path.basename(path2)
            target1 = os.path.join(conf.target, name1)
            target2 = os.path.join(conf.target, name2)
            with open(target1, 'w') as f:
                f.write(text1.encode('utf-8'))
            with open(target2, 'w') as f:
                f.write(text2.encode('utf-8'))


if __name__ == '__main__':
    main()
