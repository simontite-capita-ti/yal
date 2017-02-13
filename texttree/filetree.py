import os
from .filepath import FilePath


def iter_files(path):
    """TODO: Docstring for iter_files.

    :path: TODO
    :returns: TODO

    """
    counter = 0
    while True:
        name = str(counter)
        next_path = os.path.join(path, name)
        yield FilePath.from_path(next_path)
        counter += 1

def iter_dirs(path):
    """TODO: Docstring for iter_dirs.

    :path: TODO
    :returns: TODO

    """
    path = os.path.abspath(path)
    counter = 0
    while True:
        name = '{:09d}'.format(counter)
        chunks = []
        while name:
            chunks.append(name[:3])
            name = name[3:]
        next_path = os.path.join(path, *chunks)
        os.makedirs(next_path)
        yield iter_files(next_path)
        counter += 1
