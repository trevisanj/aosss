#!/usr/bin/env python3

"""Spectrum List Editor"""

import sys
import argparse
import astroapi as aa
import aosss as ao
import logging


aa.logging_level = logging.INFO
aa.flag_log_file = True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=aa.SmartFormatter
    )
    parser.add_argument('fn', type=str, help="file name, supports '%s' only at the moment" %
                                             (ao.FileSpectrumList.description,), nargs='?')
    args = parser.parse_args()

    app = aa.get_QApplication([])
    form = ao.XFileSpectrumList()

    if args.fn is not None:
        form.load_filename(args.fn)

    form.show()
    sys.exit(app.exec_())
