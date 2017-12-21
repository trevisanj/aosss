"""
Basic routines, they don't use anything from parent module
"""


import numpy as np
import aosss.physics as ph

__all__ = ["sparse_cube_to_colors"]

def sparse_cube_to_colors(scube, visible_range=None, flag_scale=False, method=0):
    """Returns a [nY, nX, 3] red-green-blue (0.-1.) matrix

    Args:
        scube:
        visible_range: if passed, the true human visible range will be
                       affine-transformed to visible_range in order
                       to use the red-to-blue scale to paint the pixels
        flag_scale: whether to scale the luminosities proportionally
                      the weight for each spectra will be the area under the flux
        method: see aosss.physics.spectrum_to_rgb()
    """
    im = np.zeros((scube.height, scube.width, 3))
    weights = np.zeros((scube.height, scube.width, 3))
    max_area = 0.
    for i in range(scube.width):
        for j in range(scube.height):
            sp = scube.get_pixel(i, j, False)
            if len(sp) > 0:
                im[j, i, :] = ph.spectrum_to_rgb(sp, visible_range, method)
                sp_area = np.sum(sp.y)
                max_area = max(max_area, sp_area)
                if flag_scale:
                    weights[j, i, :] = sp_area
    if flag_scale:
        weights *= 1. / max_area
        im *= weights
    return im

