#!/usr/bin/env python3

"""Data Cube Editor, import/export WebSim-COMPASS data cubes"""

import sys
import argparse
import astroapi as aa
import logging


aa.logging_level = logging.INFO
aa.flag_log_file = True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=aa.SmartFormatter
    )
    parser.add_argument('fn', type=str, nargs='?',
                        #default=FileSparseCube.default_filename,
     help="file name, supports '%s' and '%s'" %
          (ao.FileSparseCube.description, ao.FileFullCube.description))

    args = parser.parse_args()

    app = aa.get_QApplication([])
    form = XFileSparseCube()

    if args.fn is not None:
        form.load_filename(args.fn)

    form.show()
    sys.exit(app.exec_())
