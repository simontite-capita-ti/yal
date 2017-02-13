import os
import logging
import subprocess
import tempfile
import shutil
import json
from collections import Counter
from texttree.texttree import walk_dir

log = logging.getLogger(__name__)
to_text_temp_path = tempfile.mkdtemp(suffix='_to_text_converter')

def to_text(in_path, out_path):
    """TODO: Docstring for to_text.

    :in_path: TODO
    :out_path: TODO
    :returns: TODO

    """
    log.info('Converting file into text file from "%s" to "%s"', in_path, out_path)
    subprocess.call([
        'soffice',
        '--headless',
        '--convert-to',
        'txt:Text',
        '--outdir',
        to_text_temp_path,
        in_path
    ])
    try:
        dirpath, _, filenames = next(os.walk(to_text_temp_path))
        converted_path = os.path.join(dirpath, filenames[0])
        shutil.copyfile(converted_path, out_path)
        os.unlink(converted_path)
    except IndexError:
        pass

def get_counter_dir(base, counter):
    name = '{:09d}'.format(counter)
    chunks = []
    while name:
        chunks.append(name[:3])
        name = name[3:]
    return os.path.join(base, *chunks)

def convert_dir(src_path, dst_path):
    """TODO: Docstring for convert_dir.

    :src_path: TODO
    :dst_path: TODO
    :returns: TODO

    """
    src_map = {}
    dir_map = {}
    dir_counter = Counter()
    path_counter = 0
    for i, src in enumerate(walk_dir(src_path)):
        _, src_ext = os.path.splitext(src)
        if not src_ext in ['.doc', '.docx']:
            log.info('Skipping unsupported file "%s"', src)
            continue
        log.info('Converting to plaintext, file %s', i+1)
        next_src_dir = os.path.dirname(src)
        if next_src_dir in dir_map:
            next_dst_path = dir_map[next_src_dir]
        else:
            next_dst_path = get_counter_dir(dst_path, path_counter)
            os.makedirs(next_dst_path)
            path_counter += 1
            dir_map[next_src_dir] = next_dst_path
        dst_name = str(dir_counter[next_dst_path])
        dst = os.path.join(next_dst_path, dst_name)
        dir_counter[next_dst_path] += 1
        to_text(src, dst)
        src_map[src] = dst
    return src_map
