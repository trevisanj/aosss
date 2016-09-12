__all__ = ["load_spectrum_from_cube"]

import numpy as np
from pyfant import *
from astropy.io import fits


def load_spectrum_from_cube(filename, x=0, y=0):
    """Loads FITS file and gets given spectrum in data cube.

    This routine intends to deal with files such as "C000793_reduced.fits" """

    hdul = fits.open(filename)

    hdu = hdul[0]

    hdu_out = fits.PrimaryHDU()
    hdu_out.header["CDELT1"] = hdu.header["CDELT3"]
    hdu_out.header["CRVAL1"] = hdu.header["CRVAL3"]
    hdu_out.data = hdu.data[:, y, x]

    ret = Spectrum()
    ret.from_hdu(hdu_out)

    return ret
