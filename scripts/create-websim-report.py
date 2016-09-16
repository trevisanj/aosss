#!/usr/bin/python
"""
Creates report for a given set of WEBSIM-COMPASS output files
"""
import argparse
from pyfant import *
from pymos import *
import logging
import glob

misc.logging_level = logging.INFO

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
     description=__doc__,
     formatter_class=SmartFormatter
    )

    parser.add_argument('simid', type=str, nargs=1,
     help="Simulation ID, e.g., 'C000793'")
    parser.add_argument('--fn_output', nargs='?', default='(automatic)', type=str,
     help='Output HTML file name')
    parser.add_argument('--dir', nargs='?', default='.', type=str,
     help='Input directory')

    args = parser.parse_args()

    fn_output = None if args.fn_output == "(automatic)" else args.fn_output

    fn_output = create_websim_report(args.simid[0], args.dir, fn_output)

    print "File '%s' created successfully" % fn_output
