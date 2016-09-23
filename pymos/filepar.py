__all__ = ["FilePar"]

from pyfant import DataFile

class FilePar(DataFile):
    class FileAbonds(DataFile):
        description = "Websim-Compass session parameters"
        default_filename = None
        attrs = []

        def __init__(self):
            DataFile.__init__(self)


        def _do_load(self, filename):
            with open(filename, "r") as f:
                s = f.readline().srip()
                if s.startswith("#"):
                    continue
                if len(s) == 0:
                    continue


        def _do_save_as(self, filename):
            raise RuntimeError("Not applicable")

