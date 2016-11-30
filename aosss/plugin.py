from aosss.datatypes import *

def setup_astroapi(aa):
    """Adds entries to the astroapi module"""

    aa.classes_bin.extend([FileFullCube, FileSparseCube, FileSpectrumList])