import logging
import itertools
import nltk.data
from nltk.tokenize.regexp import WordPunctTokenizer
from texttree.texttree import walk_dir


log = logging.getLogger(__name__)
sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
tokenizer = WordPunctTokenizer()

def convert_dir_in_place(path):
    """TODO: Docstring for convert_dir_in_place.

    :path: TODO
    :returns: TODO

    """
    for i, next_path in enumerate(walk_dir(path)):
        log.info('Tokenizing file %s, "%s"', i+1, next_path)
        # 1. each new line is sentence
        with open(next_path) as f:
            recs = list(f)
        recs = (r.decode('utf-8') for r in recs)
        recs = (r.strip() for r in recs)
        # 2. split sentences inside each new line
        recs = (sent_detector.tokenize(r) for r in recs)
        recs = itertools.chain.from_iterable(recs)
        # 3. tokenize each sentence skipping empty one
        recs = (tokenizer.tokenize(r) for r in recs if r)
        # 4. saving file inplace
        with open(next_path, 'w') as f:
            for rec in recs:
                if rec:
                    rec = (r.encode('utf-8') for r in rec if r)
                    f.write(' '.join(rec))
                    f.write('\n')
