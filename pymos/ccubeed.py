#!/usr/bin/python

"""WebSim Compass FITS cube editor"""

from a_XFileCCube import *
from fileccube import *
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
    parser.add_argument('fn', type=str, help='%s file name' % FileCCube.description, nargs='?')
    args = parser.parse_args()

    app = get_QApplication([])
    form = XFileCCube()

    if args.fn is not None:
        fn = args.fn[0]
        if len(args.fn) > 1:
            print "Additional filenames ignored: %s" % (str(args.fn[1:]),)
        m = FileCCube()
        m.load(args.fn)

        form.load(m)

    form.show()
    sys.exit(app.exec_())
