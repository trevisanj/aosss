'''"Adaptive Optics Systems Simulation Support"'''

# # Imports
from . import physics
from .physics import *
from .basic import *
from .blocks import *
from .filetypes import *
from .util import *
from .report import *
from .mosaic import *
from .vis import *
from .gui import *

# # Function to access package-specific config file
def get_config():
    """Returns AAConfigObj object that corresponds to file ~/.f311.aosss.conf"""
    import a99
    return a99.get_config_obj(".aosss.conf")


