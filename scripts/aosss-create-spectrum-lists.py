#!/usr/bin/env python3

"""
Create several .splist files, grouping spectra by their wavelength vector

All spectra in each .splist file must have the same wavelength vector
"""


import glob
import os
from pyfant import *
from aosss import *
import re
import numpy as np
import logging
import argparse
from pyfant import *
from aosss import *
import logging
import glob


misc.logging_level = logging.INFO


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
     description=__doc__,
     formatter_class=SmartFormatter
    )

    parser.add_argument('--stage', type=str, nargs='?', default="spintg",
     help="Websim-Compass pipeline stage (will collect files named, e.g., C000793_<stage>.fits)")

    args = parser.parse_args()

    create_spectrum_lists(".", args.stage)



