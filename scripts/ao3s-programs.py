#!/usr/bin/python

"""Lists all programs available with `ao3s` package"""

from pyfant import *
from ao3s import *
import argparse
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=SmartFormatter
    )
    parser.add_argument('format', type=str, help='Print format', nargs="?", default="text",
                        choices=["text", "markdown-list", "markdown-table"])
    args = parser.parse_args()

    p = get_ao3s_scripts_path()
    scriptinfo = get_script_info(p)

    if len(scriptinfo) == 0:
        print "No scripts found in '%s'" % p
    else:
        linesp, module_len = format_script_info(scriptinfo, format=args.format)

        print "\n".join(linesp)

