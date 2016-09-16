__all__ = ["create_websim_report"]

import os
from astropy.io import fits
from pyfant import *
from matplotlib import pyplot as plt
# import glob


###############################################################################
# # HTML fragment generation routines
# Block routines (e.g., head, h1) result should always end with a "\n".
# Inline tags, NOT.

def _head(title):
    """Returns the "head" section of HTML"""

    return """<!DOCTYPE html>
<html>
<head>
  <title>%s</title>
</head>
""" % title

def _h(title, n=1):
    """Creates "h<n>" tag"""
    return "<h%d>%s</h%d>\n" % (n, title, n)

# FITS files: <simid>+"_"+_fitss[i]+".fits"
_fitss = ["cube_hr", "cube_seeing", "ifu_noseeing", "mask_fiber_in_aperture",
          "reduced", "reduced_snr", "sky", "skysub", "spintg", "spintg_noseeing",
          "therm", "aparicio"]

def _color(s, color):
    """Returns inline colored text"""
    return '<span style="color: %s">%s</span>' % (color, s)

###############################################################################


def create_websim_report(simid, dir_=".", fn_output=None):
    """Creates HTML output and several PNG files with coherent naming

    Returns:
        fn_output

    Arguments:
      simid -- simulation ID. This should be a string starting with a "C", e.g.,
        "C000793"
      dir_ -- directory containing the simulation ouput files
      fn_out -- (optional) path to HTML output file. If not passed, name will be
        made automatically as "./report-"+(simulation ID)+".html"
    """

    if simid[0] != "C":
        raise RuntimeError("Simulation ID must start with a 'C' letter")

    # # Setup

    # file_prefix: common start to all filenames generated
    if fn_output == None:
        file_prefix = "./report-"+simid
        fn_output = file_prefix + ".html"
    else:
        file_prefix, _ = os.path.splitext(fn_output)
    f_fn_fits = lambda middle: os.path.join(dir_, "%s_%s.fits" % (simid, middle))
    filelist = []

    # My first generator!!!
    def gen_fn_fig():
        cnt = 0
        while True:
            yield "%s-%03d.png" % (file_prefix, cnt)
            cnt += 1
    next_fn_fig = gen_fn_fig()

    # # HTML Generation

    with open(fn_output, "w") as html:
        html.write(_head("Simulation %s" % simid))
        html.write(_h("Simulation # %s" % simid))

        html.write(_h("1. File list", 2))
        l_s = ["<ul>\n"]
        for middle in _fitss:
            fn = f_fn_fits(middle)
            l_s.append("  <li>"+fn)
            if not os.path.isfile(fn):
                l_s.append(" (not present)")
            else:
                filelist.append(fn)
            l_s.append("</li>\n")
        l_s.append("</ul>\n")
        html.write("".join(l_s))
        filelist.sort()  # guarantees that 'spintg' comes before 'spintg_noseeing' and 'therm'


        # html.write(_h("2. FITS headers", 2))
        html.write(_h("2. File Contents", 2))
        html.write('<table style="border: 6px solid #003000;">\n')
        for fn in filelist:
            html.write('<tr>\n<td style="text-align: right; vertical-align: top; border-bottom: 3px solid #003000;">\n')
            html.write("<b>%s</b>" % fn)
            html.write('</td>\n<td style="vertical-align: top; border-bottom: 3px solid #003000;">\n')
            try:
                with fits.open(fn) as hdul:
                    hdul.verify()
                    try:
                        s_h = repr(hdul[0].header)
                    except:
                        # Apparently, on the second time, it works if does not on the first time
                        s_h = repr(hdul[0].header)
                html.write("<pre>%s</pre>\n" % s_h)
            except:
                get_python_logger().exception("Failed to dump header from file '%s'" % fn)
                html.write(_color("Header dump failed", "red"))
            html.write("</td>\n")


            print "Generating visualization for file '%s' ..." % fn
            html.write('<td style="vertical-align: top; border-bottom: 3px solid #003000; text-align: center">\n')
            try:
                fig = None
                fileobj = None

                if ("spintg_noseeing" in fn) or ("therm" in fn):
                    sp = load_spectrum_fits_messed_x(fn, sp_ref)
                    if sp:
                        fileobj = FileSpectrum()
                        fileobj.spectrum = sp
                else:
                    fileobj = load_any_file(fn)

                if isinstance(fileobj, FileWebsimCube) and (not "cube_seeing" in fn):
                    # note: skips "ifu_seeing" because it takes too long to renderize
                    fig = plt.figure()
                    ax = fig.gca(projection='3d')
                    datacube = DataCube()
                    datacube.from_websim_cube(fileobj.wcube)
                    draw_cube_3d(ax, datacube)
                    fig.tight_layout()
                elif isinstance(fileobj, FileSpectrum):
                    if "spintg." in fn:
                        sp_ref = fileobj.spectrum
                    fig = draw_spectra([fileobj.spectrum])
                    # https://github.com/matplotlib/matplotlib/issues/2305/
                    DPI = float(fig.get_dpi())
                    fig.set_size_inches(640./DPI, 270./DPI)
                    fig.tight_layout()

                if fig:
                    fn_fig = next_fn_fig.next()
                    # print "GONNA SAVE FIGURE AS "+str(fn_fig)
                    fig.savefig(fn_fig)
                    html.write('<img src="%s"></img>' % fn_fig)
                elif fileobj:
                    html.write("(visualization not available for this file (class: %s)" % fileobj.__class__.description)
                else:
                    html.write("(could not load file)")
            except:
                get_python_logger().exception("Failed to load file '%s'" % fn)
                html.write(_color("Header dump failed", "red"))
            html.write("</td>\n")





            html.write("</tr>\n")
        html.write("</table>\n")












        # html.write(_h("3. Visualization", 2))
        # html.write('<table style="border: 6px solid #003000;">\n')
        # for fn in filelist:
        #     print "Generating visualization for file '%s' ..." % fn
        #     html.write('<tr>\n<td style="text-align: right; vertical-align: top; border-bottom: 2px solid #003000;">\n')
        #     html.write(_h(fn, 3))
        #     html.write('</td>\n<td style="border-bottom: 2px solid #003000; text-align: center">\n')
        #     try:
        #         fig = None
        #         fileobj = None
        #
        #         if ("spintg_noseeing" in fn) or ("therm" in fn):
        #             sp = load_spectrum_fits_messed_x(fn, sp_ref)
        #             if sp:
        #                 fileobj = FileSpectrum()
        #                 fileobj.spectrum = sp
        #         else:
        #             fileobj = load_any_file(fn)
        #
        #         if isinstance(fileobj, FileWebsimCube) and (not "cube_seeing" in fn):
        #             # note: skips "ifu_seeing" because it takes too long to renderize
        #             fig = plt.figure()
        #             ax = fig.gca(projection='3d')
        #             datacube = DataCube()
        #             datacube.from_websim_cube(fileobj.wcube)
        #             draw_cube_3d(ax, datacube)
        #             fig.tight_layout()
        #         elif isinstance(fileobj, FileSpectrum):
        #             if "spintg." in fn:
        #                 sp_ref = fileobj.spectrum
        #             fig = draw_spectra([fileobj.spectrum])
        #             # https://github.com/matplotlib/matplotlib/issues/2305/
        #             DPI = float(fig.get_dpi())
        #             fig.set_size_inches(640./DPI, 270./DPI)
        #             fig.tight_layout()
        #
        #         if fig:
        #             fn_fig = next_fn_fig.next()
        #             # print "GONNA SAVE FIGURE AS "+str(fn_fig)
        #             fig.savefig(fn_fig)
        #             html.write('<img src="%s"></img>' % fn_fig)
        #         elif fileobj:
        #             html.write("(visualization not available for this file (class: %s)" % fileobj.__class__.description)
        #         else:
        #             html.write("(could not load file)")
        #     except:
        #         get_python_logger().exception("Failed to load file '%s'" % fn)
        #         html.write(_color("Header dump failed", "red"))
        #     html.write("</td>\n</tr>\n")
        # html.write("</table>\n")

    return fn_output
