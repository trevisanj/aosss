#!/usr/bin/env python

"""Spectrum List Editor"""

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
    parser.add_argument('fn', type=str, help="file name, supports '%s' only at the moment" %
                                             (aosss.FileSpectrumList.description,), nargs='?')
    args = parser.parse_args()

    app = a99.get_QApplication([])
    form = aosss.XFileSpectrumList()

    if args.fn is not None:
        form.load_filename(args.fn)

    form.show()
    sys.exit(app.exec_())
