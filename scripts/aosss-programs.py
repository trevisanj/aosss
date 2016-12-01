#!/usr/bin/env python3


"""Lists all programs available with `aosss` package"""


import argparse
import logging
import aosss
import astroapi as aa


aa.logging_level = logging.INFO
aa.flag_log_file = True


# TODO see if can merge
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=aa.SmartFormatter
    )
    parser.add_argument('format', type=str, help='Print format', nargs="?", default="text",
                        choices=["text", "markdown-list", "markdown-table"])
    args = parser.parse_args()

    p = aosss.get_aosss_scripts_path()
    scriptinfo = aa.get_script_info(p)

    if len(scriptinfo) == 0:
        print(("No scripts found in '%s'" % p))
    else:
        linesp, module_len = aa.format_script_info(scriptinfo, format=args.format)

        print(("\n".join(linesp)))

