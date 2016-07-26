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
from pymos.misc import *


class SpectrumCollection(AttrsPart):
    """Base class, maintains spectra with "more headers", HDU transfer without much interpretation"""
    attrs = ["fieldnames", "more_headers", "spectra"]

    def __init__(self):
        AttrsPart.__init__(self)
        self._flag_created_by_block = False  # assertion
        self.filename = None
        # _LambdaReference instance, can be inferred from first spectrum added
        self.spectra = []
        # List of field names
        self.fieldnames = []
        self.more_headers = {}

    def __len__(self):
        return len(self.spectra)

    # NAXIS(1/2/3) apparently managed by pyfits
    _IGNORE_HEADERS = ("NAXIS", "FIELDNAM")
    def from_hdulist(self, hdul):
        assert isinstance(hdul, fits.HDUList)
        if not (hdul[0].header.get("ANCHOVA") or hdul[0].header.get("TAINHA")):
            raise RuntimeError("Wrong HDUList")

        self.spectra = []
        for i, hdu in enumerate(hdul):
            if i == 0:            
                # Additional header fields
                for name in hdu.header:
                    if not name.startswith(self._IGNORE_HEADERS):
                        self.more_headers[name] = hdu.header[name]
                
                temp = hdu.header.get("FIELDNAM", [])
                if temp:
                    self.fieldnames = eval_fieldnames(temp)
            else:
                sp = Spectrum()
                sp.from_hdu(hdu)
                self.add_spectrum(sp)

    def to_hdulist(self):
        # I think this is not or should not be a restriction assert len(self.spectra) > 0, "No spectra added"

        dl = self.delta_lambda

        hdul = fits.HDUList()

        hdu = fits.PrimaryHDU()
        hdu.header["FIELDNAM"] = str(self.fieldnames)
        hdu.header["ANCHOVA"] = 26.9752

        hdu.header.update(self.more_headers)  # TODO hope this works, if not ...
#        for name, value in self.more_headers.iteritems():
#            hdu.header[name] = value

        hdul.append(hdu)

        for sp in self.spectra:
            hdul.append(sp.to_hdu())

        return hdul

    def collect_fieldnames(self):
        """Returns a list of unique field names union'ing all spectra field names"""
        # self.fieldnames = []
        ff = []
        for sp in self.spectra:
            ff.extend(sp.more_headers.keys())
        return list(set(ff))

    def add_spectrum(self, sp):
        """Adds spectrum, no content check"""
        assert isinstance(sp, Spectrum)
        self.spectra.append(sp)

    def delete_spectra(self, indexes):
        """Deletes spectra given a list of 0-based indexes"""
        if isinstance(indexes, numbers.Integral):
            indexes = [indexes]
        indexes = list(set(indexes))
        n = len(self.spectra)
        if any([idx < 0 or idx >= n for idx in indexes]):
            raise RuntimeError("All indexes must be (0 le index lt %d)" % n)
        for index in reversed(indexes):
            del self.spectra[index]


class SpectrumList(SpectrumCollection):
    attrs = SpectrumCollection.attrs+["wavelength"]

    @property
    def delta_lambda(self):
        return self.wavelength[1]-self.wavelength[0]

    @property
    def flag_wled(self):
        """Wavelength problem already resolved?"""
        return self.wavelength[0] > -1

    def __init__(self, hdulist=None):
        SpectrumCollection.__init__(self)
        self.__flag_update = True
        self.__flag_update_pending = False
        self.wavelength = np.array([-1., -1.])  # the wavelength axis (angstrom) (shared among all spectra in the cube)

        if hdulist is not None:
            self.from_hdulist(hdulist)

    ############################################################################
    # # Interface

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
        self.__flag_update = False
        try:
            SpectrumCollection.from_hdulist(self, hdul)
        finally:
            self.enable_update()

    def to_colors(self, visible_range=None, flag_scale=False, method=0):
        """Returns a [n, 3] red-green-blue (0.-1.) matrix

        Arguments:
          visible_range=None -- if passed, the true human visible range will be
                                affine-transformed to visible_range in order
                                to use the red-to-blue scale to paint the pixels
          flag_scale -- whether to scale the luminosities proportionally
                        the weight for each spectra will be the area under the flux
          method -- see Spectrum.get_rgb()
        """
        weights = np.zeros((len(self), 3))
        max_area = 0.
        ret = np.zeros((len(self), 3))
        for i, sp in enumerate(self.spectra):
            ret[i, :] = sp.get_rgb(visible_range, method)
            sp_area = np.sum(sp.y)
            max_area = max(max_area, sp_area)
            weights[i, :] = sp_area
        if flag_scale:
            weights *= 1./max_area
            ret *= weights
        # TODO return weights if necessary
        return ret

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

        SpectrumCollection.add_spectrum(self, sp)
        self.__update()

    def delete_spectra(self, indexes):
        SpectrumCollection.delete_spectra(indexes)
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
    description = "Spectrum List"
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
