""""
List of spectra sharing same wavenumber axis. Uses FITS format
"""

__all__ = ["SpectrumList", "FileSpectrumList"]

from pyfant import DataFile, AttrsPart, Spectrum, cut_spectrum_idxs, cut_spectrum
from pyfant import get_python_logger
import numpy as np
from pyfant.misc import *
from astropy.io import fits
import os
from fileccube import *
import numpy as np
from scipy.interpolate import interp1d
import numbers

_MMM = [("hr_pix_size", "CDELT1"),
        ("hrfactor", "HRFACTOR"),
        ("R", "R")]


class SpectrumList(AttrsPart):
    attrs = ["wavelength", "spectra"]

    @property
    def delta_lambda(self):
        return self.wavelength[1]-self.wavelength[0]

    @property
    def flag_wled(self):
        """Wavelength problem already resolved?"""
        return self.wavelength[0] > -1

    def __init__(self, hdu=None):
        AttrsPart.__init__(self)
        self._flag_created_by_block = False  # assertion
        self.__flag_update = True
        self.__flag_update_pending = False
        self.hdu = None  # PyFITS HDU object
        self.wavelength = np.array([-1., -1.])  # the wavelength axis (angstrom) (shared among all spectra in the cube)
        self.filename = None
        # Header data initialized to default
        self.R = 5000
        self.hrfactor = 10
        self.hr_pix_size = 0.0375/self.hrfactor
        self.width = 50
        self.height = 30
        # _LambdaReference instance, can be inferred from first spectrum added
        self.spectra = []

        if hdu is not None:
            self.from_hdu(hdu)

    def __len__(self):
        return len(self.spectra)

    def __repr__(self):
        return "Please implement SpectrumList.__repr__()"

    def matrix(self):
        """Returns a (spectrum)x(wavelength) matrix of flux values"""
        n = len(self)
        if n == 0:
            return np.array()
        return np.vstack([sp.y for sp in self.spectra])

    def crop(self, lambda0=None, lambda1=None):
        """
        Cuts all spectra

        **Note** lambda1 **included** in interval (not pythonic).
        """
        if len(self.spectra) == 0:
            raise RuntimeError("Need at least one spectrum added in order to crop")

        if lambda0 is None:
            lambda0 = self.wavelength[0]
        if lambda1 is None:
            lambda1 = self.wavelength[-1]
        if not (lambda0 <= lambda1):
            raise RuntimeError('lambda0 must be <= lambda1')

        if not any([lambda0 != self.wavelength[0], lambda1 != self.wavelength[-1]]):
            return

        for i in range(len(self)):
            sp = cut_spectrum(self.spectra[i], lambda0, lambda1)
            if i == 0:
                n = len(sp)
                if n < 2:
                    raise RuntimeError("Cannot cut, spectrum will have %d point%s" % (n, "" if n == 1 else "s"))
            self.spectra[i] = sp

        self.__update()

    def from_hdulist(self, hdul):
        assert isinstance(hdul, fits.HDUList)
        try:
            test = hdul[0].header["ANCHOVA"]
        except KeyError:
            raise RuntimeError("Wrong HDUList")

        self.spectra = []

        self.__flag_update = False
        try:
            for i, hdu in enumerate(hdul):
                if i == 0:
                    lambda0, lambda1, delta_lambda = [hdu.header[x] for x in "LAMBDA0", "LAMBDA1", "DELTA_LA"]
                    if delta_lambda > 0:
                        self.wavelength = np.arange(lambda0, lambda1 + delta_lambda, delta_lambda)
                    else:
                        self.wavelength = np.array([-1, -1])
                else:
                    sp = Spectrum()
                    sp.from_hdu(hdu)
                    self.add_spectrum(sp)
        finally:
            self.enable_update()

    def to_colors(self, visible_range=None, flag_scale=True):
        """Returns a [n, 3] red-green-blue (0.-1.) matrix

        Arguments:
          visible_range=None -- if passed, the true human visible range will be
                                affine-transformed to visible_range in order
                                to use the red-to-blue scale to paint the pixels
          flag_scale -- whether to scale the luminosities proportionally
                        the weight for each spectra will be the area under the flux
        """
        weights = np.zeros((len(self), 3))
        max_area = 0.
        ret = np.zeros((len(self), 3))
        for i, sp in enumerate(self.spectra):
            ret[i, :] = sp.get_rgb(visible_range)
            sp_area = np.sum(sp.y)
            max_area = max(max_area, sp_area)
            weights[i, :] = sp_area
        if flag_scale:
            weights *= 1./max_area
            ret *= weights
        return ret

    def to_hdulist(self):
        # I think this is not or should not be a restriction assert len(self.spectra) > 0, "No spectra added"

        dl = self.delta_lambda

        hdul = fits.HDUList()

        hdu = fits.PrimaryHDU()
        hdu.header["LAMBDA0"] = self.wavelength[0]
        hdu.header["LAMBDA1"] = self.wavelength[-1]
        hdu.header["DELTA_LA"] = dl
        hdu.header["ANCHOVA"] = 26.9752
        hdul.append(hdu)

        for sp in self.spectra:
            hdu = fits.PrimaryHDU()
            hdu.header["CDELT1"] = dl
            hdu.header["CRVAL1"] = sp.x[0]  # **note** not subtracting dl as required in WebSimCompass format
            hdu.data = sp.y
            hdul.append(hdu)

        return hdul

    def add_spectrum(self, sp):
        """Adds spectrum, checks if wavelengths match first"""
        assert isinstance(sp, Spectrum)
        if len(sp.x) < 2:
            raise RuntimeError("Spectrum must have at least two points")
        if not self.flag_wled:
            self.wavelength = np.copy(sp.wavelength)
        else:
            if not np.all(self.wavelength == sp.wavelength):
                raise RuntimeError("Cannot add spectrum, wavelength vector does not match existing")

        self.spectra.append(sp)
        self.__update()

    def delete_spectra(self, indexes):
        indexes = list(set(indexes))
        if isinstance(indexes, numbers.Integral):
            indexes = [indexes]
        for index in reversed(indexes):
            del self.spectra[index]
        self.__update()

    def enable_update(self):
        self.__flag_update = True
        if self.__flag_update_pending:
            self.__update()
            self.__flag_update_pending = False

    def __update(self):
        """Updates internal state"""

        if not self.__flag_update:
            self.__flag_update_pending = True
            return

        if len(self.spectra) == 0:
            return

        # Nothing to update so far
        pass


class FileSpectrumList(DataFile):
    """Represents a Spectrum List file, which is also a FITS file"""
    attrs = ['splist']
    description = "Spectrum List FITS cube"
    default_filename = "default.splist.fits"

    def __init__(self):
        DataFile.__init__(self)
        self.splist = SpectrumList()

    def _do_load(self, filename):
        fits_obj = fits.open(filename)
        self.splist = SpectrumList()
        self.splist.from_hdulist(fits_obj)
        self.filename = filename

    def _do_save_as(self, filename):
        if os.path.isfile(filename):
            os.unlink(filename)  # PyFITS does not overwrite file
        hdul = self.splist.to_hdulist()
        hdul.writeto(filename)

    def init_default(self):
        # Already created OK
        pass
