import os
from .filepath import FilePath

def walk_dir(root):
    """TODO: Docstring for walk_dir.

    :root: TODO
    :returns: TODO

    """
    root = os.path.abspath(root)
    for dirpath, dirnames, filenames in os.walk(root):
        for filename in filenames:
            yield os.path.join(dirpath, filename)

def walk_file_lists(root):
    """TODO: Docstring for walk_file_lists.

    :root: TODO
    :returns: TODO

    """
    root = os.path.abspath(root)
    for dirpath, dirname, filenames in os.walk(root):
        paths = []
        for next_name in filenames:
            paths.append(
                FilePath.from_path(os.path.join(dirpath, next_name))
            )
        if paths:
            yield paths

def walk_file_lang_pairs(root, langs):
    """TODO: Docstring for walk_file_lang_pairs.

    :root: TODO
    :langs: list of languages to iterate
    :returns: TODO

    """
    for paths in walk_file_lists(root):
        path_langs = {}
        for path in paths:
            name, lang = path.name.split('.')
            path_langs.setdefault(name, {})[lang] = path
        next_pairs = {}
        for _, pair_files in path_langs.items():
            next_pairs = {}
            for lang in langs:
                if lang in pair_files:
                    next_pairs[lang] = pair_files[lang]
                else:
                    break
            else:
                yield next_pairs
