#!/usr/bin/env python3

"""
Creates report for a given set of WEBSIM-COMPASS output files
"""


import argparse
import logging
import glob
import os
import pyfant
import aosss
import sys


pyfant.logging_level = logging.INFO


if __name__ == "__main__":
    lggr = pyfant.get_python_logger()

    parser = argparse.ArgumentParser(
     description=__doc__,
     formatter_class=pyfant.SmartFormatter
    )

    parser.add_argument('--dir', nargs='?', default='.', type=str,
     help='Input directory')
    parser.add_argument('--max', metavar='N', type=int, default=100,
                        help='Maximum allowed number of reports')
    parser.add_argument('numbers', metavar='N', type=str, nargs='+',
                     help='List of simulation numbers (single value and ranges accepted, e.g. 1004, 1004-1040)')

    args = parser.parse_args()

    simids0 = aosss.compile_simids(args.numbers)

    # Checks which ones actually exist in directory
    simids = []
    for simid in simids0:
        ff = glob.glob(os.path.join(args.dir, "%s*" % simid))
        if len(ff) > 0:
            simids.append(simid)

    lggr.info("List of simulation IDs: " + ", ".join(simids))

    if len(simids) > args.max:
        lggr.critical("Number of simulations to report (%d) exceeds "
                                            "maximum number (%d)" % (len(simids), args.max))
        lggr.critical("Use --max option to raise this maximum number")
        sys.exit()

    for simid in simids:
        lggr.info("Creating report for simulation '{}'...".format(simid))
        fn_output = aosss.create_simulation_report(simid, args.dir)
        lggr.info("File '%s' created successfully" % fn_output)