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


def print2(s):
  """function to standarde message lines."""
  print('GET-COMPASS: %s' % s)


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


    print(args.numbers)

    numbers = []
    for candidate in args.numbers:
        try:
            if '-' in candidate:
                groups = re.match('(\d+)\s*-\s*(\d+)$', candidate)
                if groups is None:
                    raise RuntimeError("Could not parse range")
                n0 = int(groups.groups()[0])
                n1 = int(groups.groups()[1])
                numbers.extend(list(range(n0, n1+1)))
            else:
                numbers.append(int(candidate))
        except Exception as E:
            print2("SKIPPED Argument '%s': %s" % (candidate, str(E)))


    numbers = set(numbers)
    simids = ["C%06d" % n for n in numbers]
    print2("List of simulation IDs: "+", ".join(simids))

    print("AAAAAAAAAAAAAAAAAAAA", args.max)

    if len(numbers) > args.max:
        print2("Number of simulations to get (%d) exceeds maximum number (%d)" % (len(numbers), args.max))
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
