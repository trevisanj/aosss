# # Imports
from .liblib import *
from .paths import *
from .datatypes import *
from .blocks import *
from .vis import *
from .misc import *
from .report import *
from .mosaic import *
from .gui import *

from . import liblib
from . import datatypes
from . import blocks
from . import vis
from . import misc
from . import report
from . import mosaic
from . import gui


# # Function to access package-specific config file
def get_config():
    """Returns AAConfigObj object that corresponds to file ~/.MY-PACKAGE-NAME.conf"""
    import astrogear as ag
    return ag.get_config_obj(".aosss.conf")


def classes_collection():
    """
    Returns list of File* classes that can be converted to a SpectrumCollection
    """
    import astrogear as ag
    return ag.classes_sp() + [FileSpectrumList, FileSparseCube, FileFullCube]

