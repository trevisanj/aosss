#!/usr/bin/python

"""
Create several .splist files, grouping spectra by their wavelength vector

All spectra in each .splist file must have the same wavelength vector
"""

import glob
import os
from pyfant import *
from ao3s import *
import re
import numpy as np
import logging

misc.logging_level = logging.INFO


create_spectrum_lists(".")



