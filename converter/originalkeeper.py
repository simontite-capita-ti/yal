import shutil
import logging
from texttree.texttree import walk_dir
from texttree.filepath import FilePath


log = logging.getLogger(__name__)

def keep_originals(src_map, path):
    """TODO: Docstring for keep_originals.

    :src_map: TODO
    :path: TODO
    :returns: TODO

    """
    path_map = dict((d, s) for s, d in src_map.items())
    for i, next_path in enumerate(walk_dir(path)):
        log.info('Copy original %s for "%s"', i+1, next_path)
        dst_path = FilePath.from_path(next_path)
        src_path = FilePath.from_path(path_map[next_path])
        orig_path = '{}__original__{}'.format(dst_path.path, src_path.ext)
        shutil.copyfile(src_path.path, orig_path)

def copy_to_originals(src_map):
    """TODO: Docstring for copy_to_originals.

    :src_map: TODO
    :returns: TODO

    """
    for i, (src, dst) in enumerate(src_map.items()):
        log.info('Copy to original %s file "%s"', i+1, dst)
        to_original_path = src + '_aligned'
        shutil.copyfile(dst, to_original_path)
