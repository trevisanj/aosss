import numpy as np


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

