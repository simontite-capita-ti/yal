import os
import attr


@attr.s
class FilePath(object):
    dirpath = attr.ib(default=attr.Factory(str))
    name = attr.ib(default=attr.Factory(str))
    ext = attr.ib(default=attr.Factory(str))
    path = attr.ib(default=attr.Factory(str))

    @staticmethod
    def from_path(path):
        """TODO: Docstring for from_path.

        :path: TODO
        :returns: TODO

        """
        dirpath = os.path.dirname(path)
        name = os.path.basename(path)
        ext = os.path.splitext(path)[1]
        return FilePath(dirpath=dirpath, name=name, ext=ext, path=path)
