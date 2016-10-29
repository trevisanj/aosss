#!/usr/bin/env python3


"""
Downloads a number of Websim-Compass simulations

Based on shell script by Mathieu Puech

**Note** Skips simulations for existing files in local directory starting with
         that simulation ID.
         Example: if it finds file(s) "C001006*", will skip simulation C001006

**Note** Does not create any directory (actually creates it but deletes later).
         All files stored in local directory!

**Note** Will work only on if os.name == "posix" (Linux, UNIX ...)
"""


import os
import argparse
import sys
from pyfant import *
import re
import glob
import aosss


def print2(s):
  """function to standarde message lines."""
  print(('GET-COMPASS: %s' % s))


if __name__ == "__main__":
    if os.name != "posix":
        print2("OS is '"+os.name+"', this script is only for 'posix' OS's, sorry.")
        sys.exit()

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=SmartFormatter)
    parser.add_argument('--max', metavar='N', type=int, default=100,
                        help='Maximum number of simulations to get')
    parser.add_argument('numbers', metavar='N', type=str, nargs='+',
                     help='List of simulation numbers (single value and ranges accepted, e.g. 1004, 1004-1040)')
    args = parser.parse_args()

    simids = aosss.compile_simids(args.numbers)
    print2("List of simulation IDs: "+", ".join(simids))

    if len(simids) > args.max:
        print2("Number of simulations to download (%d) exceeds maximum number (%d)" % (len(simids), args.max))
        print2("Use --max option to raise this maximum number")
        sys.exit()

    # Part based on Mathieu Puech's script
    site = "http://websim-compass.obspm.fr/wcompass"
    for simid in simids:
        ff = glob.glob("%s*" % simid)
        if len(ff) > 0:
            print2("Files found starting with '%s', skipping this download" % simid)
        print2("Downloading %s simulation files..." % simid)
        os.system("wget -v -r -l1 -np -nd -erobots=off -P %s -A.fits -A.par %s/%s/" % (simid, site, simid))
        os.system("wget -v -P %s %s/%s.out" % (simid, site, simid))
        os.system("mv %s/* ." % simid)
        os.system("rm -r %s" % simid)
