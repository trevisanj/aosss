__all__ = ["create_websim_report"]

import os
from astropy.io import fits
from pyfant import *
from matplotlib import pyplot as plt
from .misc import *
import numpy as np
import traceback

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
FILE_KEYWORDS = ["cube_hr", "cube_seeing", "ifu_noseeing", "mask_fiber_in_aperture",
          "reduced", "reduced_snr", "sky", "skysub", "spintg", "spintg_noseeing",
          "therm"]

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
    flag_log, fn_log = True, "%s.out" % simid



# TODO probably load_par separate
# TODO probably load_all_fits() instead of load_bulk()
    items = load_bulk(simid, dir_)

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
        l_s = ["<pre>\n"]
        for item in items:
            l_s.append(item.filename+(" (not present)" if not item.flag_exists else "")+"\n")

        # Log file is an extra case
        l_s.append(fn_log)
        if not os.path.isfile(fn_log):
            l_s.append(" (not present)")
        l_s.append("\n")

        l_s.append("</pre>\n")
        html.write("".join(l_s))

# TODO probably the .par file will be treated separately


        # html.write(_h("2. FITS headers", 2))
        html.write(_h("2. FITS files", 2))
        html.write('<table style="border: 6px solid #003000;">\n')
        for item in items:
            html.write('<tr>\n<td style="text-align: right; vertical-align: top; border-bottom: 3px solid #003000;">\n')
            html.write("<b>%s</b>" % item.filename)
            html.write('</td>\n<td style="vertical-align: top; border-bottom: 3px solid #003000;">\n')
            try:
                # Opens as fits to dump header
                with fits.open(item.filename) as hdul:
                    hdul.verify()
                    try:
                        s_h = repr(hdul[0].header)
                    except:
                        # Apparently, on the second time, it works if does not on the first time
                        s_h = repr(hdul[0].header)
                html.write("<pre>%s</pre>\n" % s_h)
            except:
                get_python_logger().exception("Failed to dump header from file '%s'" % item.filename)
                html.write(_color("Header dump failed", "red"))
            html.write("</td>\n")


            print "Generating visualization for file '%s' ..." % item.filename
            html.write('<td style="vertical-align: top; border-bottom: 3px solid #003000; text-align: center">\n')
            try:
                fig = None

                if isinstance(item.fileobj, FileWebsimCube) and (not "cube_seeing" in item.filename):
                    # note: skips "ifu_seeing" because it takes too long to renderize
                    fig = plt.figure()
                    ax = fig.gca(projection='3d')
                    datacube = DataCube()
                    datacube.from_websim_cube(item.fileobj.wcube)
                    draw_cube_3d(ax, datacube)
                    fig.tight_layout()
                elif isinstance(item.fileobj, FileSpectrum):
                    if item.keyword == "spintg":
                        sp_ref = item.fileobj.spectrum
                    fig = draw_spectra([item.fileobj.spectrum])
                    set_figure_size(fig, 640, 270)
                    fig.tight_layout()
                elif isinstance(item.fileobj, FileFits):
                    if item.keyword == "mask_fiber_in_aperture":
                        fig = _draw_mask(item.fileobj)
                    elif item.keyword == "cube_seeing":
                        fig = _draw_field(item.fileobj)

                if fig:
                    fn_fig = next_fn_fig.next()
                    # print "GONNA SAVE FIGURE AS "+str(fn_fig)
                    fig.savefig(fn_fig)
                    html.write('<img src="%s"></img>' % fn_fig)
                elif item.fileobj:
                    html.write("(visualization not available for this file (class: %s)" % item.fileobj.__class__.description)
                else:

# TODO I already have the error information, so can improve this

                    html.write("(could not load file)")
            except Exception as E:
                get_python_logger().exception("Failed to load file '%s'" % item.filename)
                html.write(_color("Visualization failed: "+str(E), "red"))
                html.write('<pre style="text-align: left">\n'+("\n".join(traceback.format_stack()))+"</pre>\n")
            html.write("</td>\n")


            html.write("</tr>\n")
        html.write("</table>\n")

        if  flag_log:
            html.write(_h("3. Log file dump", 2))
            html.write("<pre>\n")
            try:
                with open(fn_log, "r") as file_log:
                    html.write(file_log.read())
            except Exception as E:
                get_python_logger().exception("Failed to dump log file '%s'" % fn_log)
                html.write("("+str(E)+")")
            html.write("</pre>\n")

    return fn_output


def _draw_mask(filefits):
    """Draws the image for the Cxxxxx_mask_fiber_in_aperture.fits file. Returns figure"""
    hdu = filefits.hdulist[0]
    fig = plt.figure()
    plt.imshow(hdu.data)
    plt.xlabel("pixel-x")
    plt.ylabel("pixel-y")
    HEIGHT = 300.
    nr, nc = hdu.data.shape
    width = HEIGHT/nr*nc
    set_figure_size(fig, width, HEIGHT)
    plt.tight_layout()
    return fig


def _draw_field(filefits):
    """Draws data cube in grayscale. Values are calculated as 2-vector-norm"""
    hdu = filefits.hdulist[0]
    data = hdu.data
    grayscale = np.linalg.norm(data, 2, 0)
    fig = plt.figure()
    plt.imshow(grayscale, cmap='Greys_r')
    plt.xlabel("pixel-x")
    plt.ylabel("pixel-y")
    HEIGHT = 300.
    nr, nc = grayscale.shape
    width = HEIGHT/nr*nc
    set_figure_size(fig, width, HEIGHT)
    plt.tight_layout()
    return fig

