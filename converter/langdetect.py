import os
import logging
import langdetect
from texttree.texttree import walk_dir

log = logging.getLogger(__name__)

def convert_dir_in_place(path):
    """TODO: Docstring for convert_dir_in_place.

    :path: TODO
    :returns: TODO

    """
    src_map = {}
    done = set()
    for i, src in enumerate(walk_dir(path)):
        if src in done:
            continue
        log.info('Detecting language of file number %s "%s"', i+1, src)
        with open(src) as f:
            text = f.read()
        lang = langdetect.detect(text)
        new_name = src + '.' + lang
        os.rename(src, new_name)
        done.add(src)
        done.add(new_name)
        src_map[src] = new_name
    return src_map
