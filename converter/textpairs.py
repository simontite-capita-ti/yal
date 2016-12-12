import logging
import os
from texttree.texttree import walk_file_lists


log = logging.getLogger(__name__)

def get_lang(path):
    """TODO: Docstring for get_lang.

    :path: TODO
    :returns: TODO

    """
    return path.path[-2:]

def convert_dir_in_place(path):
    """TODO: Docstring for convert_dir_in_place.

    :path: TODO
    :returns: TODO

    """
    src_map = {}
    for i, paths in enumerate(walk_file_lists(path)):
        log.info('Finding pairs in folder, %s, "%s"', i+1, paths[0].dirpath) 
        sizes = []
        for path in paths:
            sizes.append((os.path.getsize(path.path), path))
        sizes.sort()
        pairs = []
        pair1 = pair2 = None
        while sizes:
            pair1 = sizes.pop()
            pair2 = None
            while sizes and pair2 is None:
                pair2 = sizes.pop()
                if get_lang(pair1[1]) == get_lang(pair2[1]):
                    os.unlink(pair1[1].path)
                    pair1 = pair2
                    pair2 = None
                else:
                    pairs.append((pair1[1], pair2[1]))
        if pair1 and not pair2:
            os.unlink(pair1[1].path)
        for pair1, pair2 in pairs:
            base = pair1.name.split('.')[0]
            name2 = pair2.name.split('.')[1]
            name2 = base + '.' + name2
            new_path2 = os.path.join(pair2.dirpath, name2)
            os.rename(pair2.path, new_path2)
            src_map[pair1.path] = pair1.path
            src_map[pair2.path] = new_path2
    return src_map

