#!/usr/bin/env python

"""Data Cube Editor, import/export WebSim-COMPASS data cubes"""

import sys
import argparse
import a99
import logging
import aosss


a99.logging_level = logging.INFO
a99.flag_log_file = True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=a99.SmartFormatter
    )
    parser.add_argument('fn', type=str, nargs='?',
                        #default=FileSparseCube.default_filename,
     help="file name, supports '%s' and '%s'" %
          (aosss.FileSparseCube.description, aosss.FileFullCube.description))

    args = parser.parse_args()

    app = a99.get_QApplication([])
    form = aosss.XFileSparseCube()

    if args.fn is not None:
        form.load_filename(args.fn)

    form.show()
    sys.exit(app.exec_())
