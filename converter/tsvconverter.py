import os
import logging
from texttree.texttree import walk_file_lang_pairs
from collections import Counter


log = logging.getLogger(__name__)

def copy_to_originals(src_map, path, langs):
    """TODO: Docstring for copy_to_originals.

    :src_map: TODO
    :returns: TODO

    """
    dir_counter = Counter()
    inv_map = dict((dst, src) for src, dst in src_map.items())
    for i, pair in enumerate(walk_file_lang_pairs(path, langs)):
        pair1 = pair[langs[0]]
        pair2 = pair[langs[1]]
        log.info('Copy TSV file %s, based on %s, %s', i+1, pair1, pair2)
        src_file = inv_map[pair1.path]
        src_dir = os.path.dirname(src_file)
        src_dir = os.path.basename(src_dir)
        target_path = '{}_aligned_{}_{}-{}.tsv'.format(src_dir, dir_counter[src_dir], langs[0], langs[1])
        dir_counter[src_dir] += 1
        target_path = os.path.join(os.path.dirname(src_file), target_path)
        with open(target_path, 'w') as f:
            with open(pair1.path) as f1, open(pair2.path) as f2:
                for rec1, rec2 in zip(f1, f2):
                    f.write(rec1.strip())
                    f.write('\t')
                    f.write(rec2.strip())
                    f.write('\n')
