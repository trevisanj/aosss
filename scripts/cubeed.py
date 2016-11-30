#!/usr/bin/env python3

"""Data Cube Editor, import/export WebSim-COMPASS data cubes"""

from astrotypes import *
from pyfant.gui.aosss import XFileSparseCube
import sys
import argparse
import logging

misc.logging_level = logging.INFO

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=SmartFormatter
    )
    parser.add_argument('fn', type=str, nargs='?',
                        #default=FileSparseCube.default_filename,
     help="file name, supports '%s' and '%s'" %
          (FileSparseCube.description, FileFullCube.description))

    args = parser.parse_args()

    app = get_QApplication([])
    form = XFileSparseCube()

    if args.fn is not None:
        form.load_filename(args.fn)

    form.show()
    sys.exit(app.exec_())
