""""
Support for WebSim-Compass FITS spectral cubes

Based on IDL source file chris_J4000.pro
"""

__all__ = ["CompassCube", "FileCCube"]

from pyfant import DataFile, AttrsPart, Spectrum
import numpy as np
#from pyfant.misc import *
from astropy.io import fits
import os

class CompassCube(AttrsPart):
    attrs = ["R", "hrfactor", "ifu_pix_size"]

    @property
    def flag_created(self):
        """Whether the data cube has already been created"""
        return self.hdu is not None

    @property
    def flag_wavelengthed(self):
        """Whether wavelength information is already present """
        return self.flag_created and self.hdu.header["CDELT3"] != -1

    def __init__(self, hdu=None):
        AttrsPart.__init__(self)
        self.hdu = None  # PyFITS HDU object
        self.wavelength = None  # the wavelength axis (angstrom) (shared among all spectra in the cube)
        self.filename = None

        if hdu is not None:
            self.from_hdu(hdu)

    def from_hdu(self, hdu):
        assert isinstance(hdu, fits.PrimaryHDU)

        # ensures all required headers are present
        keys = ["NAXIS1", "NAXIS2", "NAXIS3", "CDELT1", "CDELT2", "CDELT3",  "CRVAL3", "HRFACTOR"]
        for key in keys:
            assert key in hdu.header, 'Key "%s" not found in headers' % key

        l0 = hdu.header["CRVAL3"]+hdu.header["CDELT3"]
        delta_lambda = hdu.header["CDELT3"]
        nlambda = hdu.header["NAXIS3"]
        self.hdu = hdu
        self.set_wavelength(np.array([l0 + k * delta_lambda for k in range(0, nlambda)]))

    def __len__(self):
        raise NotImplementedError()

    def __repr__(self):
        return "Please implement CompassCube.__repr__()"

    def create1(self, R, dims, hr_pix_size, hrfactor):
        """Creates FITS HDU, including the cube full with zeros 

          dims -- (nlambda, height, width)
        """
        cube = np.zeros(dims)
        hdu = fits.PrimaryHDU()
        hdu.header["CDELT1"] = hr_pix_size
        hdu.header["CDELT2"] = hr_pix_size
        hdu.header["CDELT3"] = -1.0  # this will become known then paint() is called for the first time
        hdu.header["CRVAL3"] = -1.0  # "
        hdu.header["HRFACTOR"] = hrfactor
        hdu.header["R"] = R
        hdu.data = cube
        self.hdu = hdu

    def get_spectrum(self, x, y):
        """
        Returns spectrum at coordinate x, y

        **Note** coordinate (x=0, y=0) corresponds to lower left pixel of cube cross-section
        """
        assert self.flag_wavelengthed

        sp = Spectrum()
        sp.x = np.copy(self.wavelength)
        sp.y = np.copy(self.hdu.data[:, y, x])

        return sp

    def set_wavelength(self, w):
        delta_lambda = w[1] - w[0]
        self.hdu.header["CDELT3"] = delta_lambda
        # dunno why the initial lambda must be one delta lambda lower than the initial lambda in the spectrum, but
        # this is how it was in the original
        self.hdu.header["CRVAL3"] = w[0] - delta_lambda
        self.wavelength = w


class FileCCube(DataFile):
    """Represents a Compass data cube file, which is also a FITS file"""
    attrs = ['ccube']
    description = "WebSim Compass FITS cube"
    default_filename = "default.ccube.fits"

    def __init__(self):
        DataFile.__init__(self)
        self.ccube = CompassCube()

    def _do_load(self, filename):
        fits_obj = fits.open(filename)
        self.ccube = CompassCube(fits_obj[0])
        self.filename = filename

    def _do_save_as(self, filename):
        assert self.ccube.flag_wavelengthed, "Cannot save before at least one pixel has been \"painted\""""
        if os.path.isfile(filename):
            os.unlink(filename)  # PyFITS does not overwrite file
        self.ccube.hdu.writeto(filename)