#!/usr/bin/env python3

"""
Create several .splist files, grouping spectra by their wavelength vector

All spectra in each .splist file must have the same wavelength vector
"""


import argparse
import logging
import aosss
import astrogear as ag


ag.logging_level = logging.INFO
ag.flag_log_file = True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
     description=__doc__,
     formatter_class=ag.SmartFormatter
    )

    parser.add_argument('--stage', type=str, nargs='?', default="spintg",
     help="Websim-Compass pipeline stage (will collect files named, e.g., C000793_<stage>.fits)")

    args = parser.parse_args()

    aosss.create_spectrum_lists(".", args.stage)


