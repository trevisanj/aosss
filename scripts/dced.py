#!/usr/bin/python

"""Data Cube Editor, import/export WebSim-COMPASS data cubes"""

from pymos import *
from pyfant import *
import sys
import argparse
import logging

misc.logging_level = logging.INFO

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=SmartFormatter
    )
    parser.add_argument('fn', type=str, help="file name, supports '%s' and '%s'" % (FileDCube.description, FileCCube.description), nargs='?')
    args = parser.parse_args()

    app = get_QApplication([])
    form = XFileSky()

    if args.fn is not None:
        form.load_filename(args.fn)

    form.show()
    sys.exit(app.exec_())
