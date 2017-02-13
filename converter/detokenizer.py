import logging
import subprocess
from texttree.texttree import walk_dir


log = logging.getLogger(__name__)

def convert_dir_in_place(detokenizer_script, path):
    """TODO: Docstring for convert_dir_in_place.

    :detokenizer_script: TODO
    :path: TODO
    :returns: TODO

    """
    for i, next_path in enumerate(walk_dir(path)):
        log.info('Detokenizing file %s, "%s"', i+1, next_path)
        with open(next_path, 'rb') as f:
            detokenized_data = subprocess.check_output([
                'perl',
                detokenizer_script
            ], stdin=f)
        with open(next_path, 'wb') as f:
            f.write(detokenized_data)
