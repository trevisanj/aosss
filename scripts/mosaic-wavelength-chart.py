#!/usr/bin/python
# -*- coding: utf8 -*-
"""
Draws a [wavelength] x [various stacked information] chart

Two modes are available:
  - GUI mode (default): opens a GUI allowing for setup parameters
  - Plot mode (--plot): plots the chart directly in default way
"""

import argparse
from pymos import *
from pyfant import *
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
import matplotlib as mpl
import numpy as np
import numbers
import os.path


###############################################################################
# # External setup
mpl.rcParams['axes.linewidth'] = 2


###############################################################################
# # local class & function library
class MyLine(object):
    def __init__(self, name, wl, width=0, position=0):
        self.name = name
        self.wl = wl if isinstance(wl, (list, tuple)) else [wl]
        self.width = width
        if width > 0 and not isinstance(wl, numbers.Number):
            raise RuntimeError("Either specify list of lines or width")
        self.position = position

def lambda_shift(lambda_0, v_radial):
    """Calculates delta_lambda due to Doppler effect given emitter wavelength and radial velocity in km/s.
    Positive radial velocity means running away from us."""
    C = 300000  # light speed in km/s
    return lambda_0*(C+v_radial)/C

class MyCoverage(object):
    """Stores data for the wavelength coverage of a certain instrument/mode etc"""
    def __init__(self, name, l0lf):
        self.name = name
        self.l0lf = l0lf  # sequence of tuples

###############################################################################
# # Data definition
NUM_SLOTS = 10
LAST_BAND = "K"
COLOR_COVERAGE = np.array([.5, .5, .5])
COLOR_GRID = np.array((.5, .5, .5))
COLOR_BAND = [0., .3, 0.]
COLOR_SPECTRUM = [.2, .2, .2]
COLOR_TELLURIC_BOX = [182./255, 234./255, 232./255]
COLOR_TEXT = (.25, .2, .2)

HA_LAMBDA = 6562.8
HA_WIDTH = lambda_shift(HA_LAMBDA, 400) - lambda_shift(HA_LAMBDA, -400)

ll = [MyLine("CaHK", 3900),
      MyLine("Sr", 4050),
      MyLine("G", 4300),
      MyLine("Mgb", [5167.32, 5172.68, 5183.6]),
      MyLine("NaD", [5889.95, 5895.92]),
      MyLine("CaI", 6162),
      MyLine(r"H$\alpha$", 6562.8, width=HA_WIDTH),
      MyLine("OI triplet", [7777.194, 7777.417, 7777.539]),
      MyLine("CaII triplet", [8498, 8542, 8662])
      ]

cc = [MyCoverage("HMM", [(4000, 18000)]),
      MyCoverage("HDM (essential)", [(10000, 18000)]),
      MyCoverage("HDM (desirable)", [(8000, 25000)]),
      MyCoverage("IGM (essential)", [(4000, 8000)]),
      MyCoverage("IGM (desirable)", [(3700, 10000)])
      ]

###############################################################################
def draw(telluric_spectra):
    l0, lf = 3000, Bands.range(LAST_BAND)[1]
    x =  np.logspace(np.log10(l0), np.log10(lf), 1000, base=10.)
    plt.figure()
    ax = plt.gca()
    ax.set_axisbelow(True)

    # # grid
    #   ====
    # http://matplotlib.org/examples/pylab_examples/major_minor_demo1.html
    majorLocator_x = MultipleLocator(1000)
    majorFormatter_x = FormatStrFormatter('%d')
    minorLocator_x = MultipleLocator(250)
    ax.xaxis.set_major_locator(majorLocator_x)
    ax.xaxis.set_major_formatter(majorFormatter_x)
    # for the minor ticks, use no labels; default NullFormatter
    ax.xaxis.set_minor_locator(minorLocator_x)

    majorLocator_y = MultipleLocator(1.)
    majorFormatter_y = FormatStrFormatter('')
    # minorLocator_x = MultipleLocator(250)
    ax.yaxis.set_major_locator(majorLocator_y)
    ax.yaxis.set_major_formatter(majorFormatter_y)
    # for the minor ticks, use no labels; default NullFormatter
    # ax.xaxis.set_minor_locator(minorLocator_x)

    g0 = plt.grid(True, which='major', axis='x', linewidth=2, linestyle=':', color=COLOR_GRID)
    plt.grid(True, which='major', axis='y', linewidth=1, linestyle='-', color=COLOR_GRID*1.5)
    plt.grid(True, which='minor', axis='x', linestyle=':', color=COLOR_GRID)


    # # bands
    #   =====
    for band_name in Bands.names():
        y = Bands.ufunc_band(band_name)(x)*.75
        plt.plot(x, y, label=band_name, c=COLOR_BAND)
        idx_max = np.argmax(y)
        ax.annotate(band_name, xy=(x[idx_max], y[idx_max]+.1),
                    horizontalalignment="center", verticalalignment="center",
                    color=COLOR_TEXT)

        if band_name == LAST_BAND:
            break

    # # Telluric features
    Y_TOP = 2
    Y_BOTTOM = Y_TOP-1+0.01
    SPECTRUM_HEIGHT = 0.9  # Height for the spectrum to span in the chart
    ax.annotate("Telluric features", xy=[l0, Y_TOP-.02], color=COLOR_TEXT, verticalalignment="top")
    for sp in telluric_spectra:
        # let ymin=0 (maybe there is no zero transmission in the spectrum,
        # it will be good to see that frequencies are not completely attenuated)
        ymax, ymin = max(sp.y), 0
        x0, x1, y0, y1 = sp.x[0], sp.x[-1], Y_BOTTOM, Y_BOTTOM+SPECTRUM_HEIGHT
        ax.fill_between([x0, x1], [y1, y1], [y0, y0], color=COLOR_TELLURIC_BOX)
        ax.plot(sp.x, (sp.y-ymin)*SPECTRUM_HEIGHT+Y_BOTTOM, c=COLOR_SPECTRUM)


    # # Chemical lines of interest (redshifted or not)
    Y_TOP = NUM_SLOTS
    COLOR_LINES = np.array([.3, 0., .3])
    for line in ll:
        if line.width > 0:
            plt.fill_between([line.wl[0]-line.width/2, line.wl[0]+line.width/2],
                             [Y_TOP, Y_TOP], [0, 0], color=COLOR_LINES, alpha=1)
            x_ann = line.wl[0]+line.width/2
        else:
            for x in line.wl:
                plt.plot([x, x], [0, Y_TOP], c=COLOR_LINES, alpha=1)
            x_ann = max(line.wl)
        plt.annotate(line.name, xy=(x_ann, Y_TOP-.2), rotation=-90, color=COLOR_TEXT)


    # # coverages
    #   =========
    HEIGHT = .7
    y = NUM_SLOTS-(1-HEIGHT)/2-1
    for coverage in cc:
        for interval in coverage.l0lf:
            x0, x1 = interval
            plt.plot([x0, x1, x1, x0, x0], [y, y, y-HEIGHT, y-HEIGHT, y], color=COLOR_COVERAGE*.5, alpha=.8)
            plt.fill_between(interval, [y, y], [y-HEIGHT, y-HEIGHT], color=COLOR_COVERAGE, alpha=.6, hatch='//')
            x_ann = interval[1]
        plt.annotate(coverage.name, xy=(x_ann+40, y-HEIGHT/2), color=COLOR_TEXT, verticalalignment="center")
        y -= 1



    plt.xlim([l0, lf])
    plt.ylim([0, NUM_SLOTS+.01])
    plt.xlabel("Wavelength ($\AA$)")
    plt.tight_layout()
    plt.show()



if __name__ == "__main__":

    parser = argparse.ArgumentParser(
     description=__doc__,
     formatter_class=SmartFormatter
    )
    parser.add_argument('--plot', action='store_const',
                        const=True, default=False,
                        help='Plot mode (default is GUI mode)')
    args = parser.parse_args()


    # Loads telluric features
    telluric_filenames = ["telluric-5000-10000.fits", "atmos_S_H.fits",
     "atmos_S_J.fits", "atmos_S_K.fits", "atmos_S_SZ.fits"]

    telluric_spectra = []
    for fn in telluric_filenames:
        path_ = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "data", fn)
        try:
            fileobj = FileSpectrumFits()
            fileobj.load(path_)
            telluric_spectra.append(fileobj.spectrum)
        except:
            get_python_logger().exception("Failed to load '%s'" % path_)



    if args.plot:
        draw(telluric_spectra)
    else:
        print "Not yet"