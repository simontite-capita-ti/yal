import logging
import subprocess
from texttree.texttree import walk_file_lang_pairs
from texttree import filetree

log = logging.getLogger(__name__)

def convert_dir(hunalign_path, src_path, dst_path, lang1, lang2):
    """TODO: Docstring for convert_dir.

    :hunalign_path: path to hualign binary
    :src_path: TODO
    :dst_path: TODO
    :lang1: first language to align
    :lang2: second language to align
    :returns: TODO

    """
    src_map = {}
    dir_map = {}
    dir_iter = filetree.iter_dirs(dst_path)
    for i, pair in enumerate(walk_file_lang_pairs(src_path, [lang1, lang2])):
        log.info('Aligning pair %i, "%s"', i+1, pair)
        path1 = pair[lang1]
        path2 = pair[lang2]
        result = subprocess.check_output([
            hunalign_path,
            '-text',
            '-utf',
            '/dev/null',
            path1.path,
            path2.path
        ])
        sentences = []
        result = result.decode('utf-8')
        for rec in result.split('\n'):
            tokens = rec.split('\t')
            if len(tokens) == 3:
                sentences.append((tokens[0], tokens[1]))
        # no need to save empty file
        if not sentences:
            continue
        # filter and strip
        sentences = [
            (s1.strip('\t\n\r\f\v \ufeff'),
             s2.strip('\t\n\r\f\v \ufeff'))
            for s1, s2 in sentences
        ]
        sentences = [(s1, s2) for s1, s2 in sentences
                     if s1 and s2 and not s1 == s2]
        if path1.dirpath not in dir_map:
            dir_map[path1.dirpath] = next(dir_iter)
        result_path = next(dir_map[path1.dirpath])
        result_file_path1 = '{}.{}'.format(result_path.path, lang1)
        result_file_path2 = '{}.{}'.format(result_path.path, lang2)
        with open(result_file_path1, 'w') as f:
            for sent in sentences:
                f.write(sent[0])
                f.write('\n')
        with open(result_file_path2, 'w') as f:
            for sent in sentences:
                f.write(sent[1])
                f.write('\n')
        src_map[path1.path] = result_file_path1
        src_map[path2.path] = result_file_path2
    return src_map
