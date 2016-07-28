__all__ = ["rubberband", "style_widget", "eval_fieldnames"]

import numpy as np
from .fileccube import CompassCube
from pyfant import *
import matplotlib
# from fileccube import *
from scipy.interpolate import interp1d
import collections


########################################################################################################################
# # GUI Auxiliar


def style_widget(spinbox, flag_changed):
    """(Paints background yellow)/(removes stylesheet)"""
    spinbox.setStyleSheet("QWidget {background-color: #FFFF00}" if flag_changed else "")


########################################################################################################################


def bc_rubber(vx):
    """Convex Polygonal Line baseline correction

    Arguments:
      vx -- vector
    """

    return vx-rubberband(vx)


def rubberband(vx):
    """
    Convex polygonal line (aka rubberbadn) whose vertices touch troughs of x
    without crossing x, where x = X[i, :], i <= 0 < no (see below).


    This was inspired on OPUS Rubberband baseline correction (RBBC) [1]. However,
    this one is parameterless, whereas OPUS RBBC asks for a number of points.

    References:
        [1] Bruker Optik GmbH, OPUS 5 Reference Manual. Ettlingen: Bruker, 2004.
    """
    pieces = [[vx[0]]]
    _rubber_pieces(vx, pieces)
    rubberband = np.concatenate(pieces)

    return rubberband


def _rubber_pieces(x, pieces):
    """Recursive function that add straight lines to list. Together, these lines form the rubberband."""
    nf = len(x)
    l = np.linspace(x[0], x[-1], nf)
    xflat = x - l
    idx = np.argmin(xflat)
    val = xflat[idx]
    if val < 0:
        _rubber_pieces(x[0:idx + 1], pieces)
        _rubber_pieces(x[idx:], pieces)
    else:
        pieces.append(l[1:])




#########################################################################################################################################
# # PLOTTERS

def plot_colors(ax, ccube):
    """
    """
    assert isinstance(ccube, CompassCube)
    data = ccube.hdu.data
    nlambda, nY, nX = data.shape


    im = np.zeros((nY, nX, 3))
    for x in range(nX):
        for y in range(nY):
            sp = ccube.get_spectrum(x, y)
            im[y, x, :] = sp.get_rgb()

    ax.imshow(im, interpolation="nearest")
    
    

########################################################################################################################

def eval_fieldnames(string_, varname="fieldnames"):
    """Evaluates string_, must evaluate to list of strings. Also converts field names to uppercase"""
    ff = eval(string_)
    if not isinstance(ff, list):
        raise RuntimeError("%s must be a list" % varname)
    if not all([isinstance(x, str) for x in ff]):
        raise RuntimeError("%s must be a list of strings" % varname)
    ff = [x.upper() for x in ff]
    return ff

