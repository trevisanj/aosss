""""
Spectral cube allocated in a way that will take less space.

Saved in FITS format, as it is small and can be opened by other programs

Based on IDL source file chris_J4000.pro
"""

__all__ = ["Sky", "FileSky"]

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


class SkySpectrumItem(object):
    def __init__(self, x, y, z, sp):
        self.x = x
        self.y = y
        self.z = z
        self.sp = sp

class _LambdaReference(object):
    def __init__(self, x):
        self.delta_lambda = x[1]-x[0]
        self.ref_lambda = x[0] % self.delta_lambda

class Sky(AttrsPart):
    attrs = ["R", "hrfactor", "hr_pix_size"]

    @property
    def delta_lambda(self):
        return self.walength[1]-self.wavelength[0]

    def __init__(self, hdu=None):
        AttrsPart.__init__(self)
        self.__flag_update = True
        self.__flag_update_pending = False
        self.hdu = None  # PyFITS HDU object
        self.wavelength = None  # the wavelength axis (angstrom) (shared among all spectra in the cube)
        self.filename = None
        # Header data initialized to default
        self.R = 5000
        self.hrfactor = 10
        self.hr_pix_size = 0.0375/self.hrfactor
        self.width = 50
        self.height = 30
        # _LambdaReference instance, can be inferred from first spectrum added
        self.reference = None
        self.spectra = []

        if hdu is not None:
            self.from_hdu(hdu)

    def __len__(self):
        raise NotImplementedError()

    def __repr__(self):
        return "Please implement SpectrumList.__repr__()"

    def crop(self, x0=None, x1=None, y0=None, y1=None, lambda0=None, lambda1=None):
        """
        Reduces region, discards spectra, cuts remaining spectra

        intervals:
            X - [x0, x1]
            Y - [y0, y1]
            wavelength - [lambda0, lambda1]

        **Note** x1, y1, lambda 1 **included** in interval (not pythonic).
        """
        if len(self.spectra) == 0:
            raise RuntimeError("Need at least one spectrum added in order to crop")

        if x0 is None:
            x0 = 0
        if x1 is None:
            x1 = self.width-1
        if y0 is None:
            y0 = 0
        if y1 is None:
            y1 = self.height-1
        if lambda0 is None:
            lambda0 = self.wavelength[0]
        if lambda1 is None:
            lambda1 = self.wavelength[-1]

        if x0 > x1:
            raise RuntimeError('x0 is greater than x1')
        if y0 > y1:
            raise RuntimeError('y0 is greater than y1')
        if lambda0 > lambda1:
            raise RuntimeError('lambda0 is greater than lambda1')

        if not any([x0 != 0, x1 != self.width-1, y0 != 0, y1 != self.height-1, lambda0 != self.wavelength[0], lambda1 != self.wavelength[-1]]):
            return

        if any([x0 != 0, x1 != self.width-1, y0 != 0, y1 != self.height-1]):
            self.width = x1-x0+1
            self.height = y1-y0+1
            for item in self.spectra:
                item.x -= x0
                item.y -= y0

            # Deletes spectra out of XY range
            for item in reversed(self.spectra):
                if not 0 <= item.x < self.width or not 0 <= item.y < self.height:
                    self.spectra.remove(item)

        if any([lambda0 != self.wavelength[0], lambda1 != self.wavelength[-1]]):
            # cuts remaining spectra
            for item in reversed(self.spectra):
                item.sp = cut_spectrum(item.sp, lambda0, lambda1)
                if len(item.sp) == 0:
                    # If spectrum is now out of range, it is deleted
                    self.spectra.remove(item)

        self.__update()


    def from_compass_cube(self, ccube):
        assert isinstance(ccube, CompassCube)
        hdu = ccube.hdu
        assert isinstance(hdu, fits.PrimaryHDU)
        data = hdu.data
        nlambda, nY, nX = data.shape

        # Reads some attributes from the headers
        # Uses self.attrs, but this is just a coincidence, may need detachment
        for na0, na1 in _MMM:
            try:
                self.__setattr__(na0, hdu.header[na1])
            except:
                get_python_logger().exception("Failed getting header '%s'" % na1)

        self.__flag_update = False
        try:
            for i in range(nX):
                for j in range(nY):
                    Yi = j + 1
                    flux0 = data[:, j, i]
                    if np.any(flux0 > 0):
                        sp_ = ccube.get_spectrum(i, j)
                        # discards edges that are zeros
                        where_positive = np.where(sp_.flux > 0)[0]
                        sp = cut_spectrum_idxs(sp_, where_positive[0], where_positive[-1]+1)
                        self.add_spectrum(i, j, sp)
        finally:
            self.enable_update()

    def from_hdulist(self, hdul):
        assert isinstance(hdul, fits.HDUList)
        try:
            test = hdul[0].header["TAINHA"]
        except KeyError:
            raise RuntimeError("Wrong HDUList")

        # in first iteration of some loop ... self.reference = _LambdaReference()

        self.spectra = []

        self.__flag_update = False
        try:
            for i, hdu in enumerate(hdul):
                if i == 0:
                    for na0, na1 in _MMM:
                        try:
                            self.__setattr__(na0, hdu.header[na1])
                        except:
                            get_python_logger().exception("Failed setting '%s' = '%s'" % (na0, na1))

                else:
                    sp = Spectrum()
                    sp.from_hdu(hdu)
                    if i == 1:
                        # TODO this must be settable, not just taken from first spectrum
                        self.reference = _LambdaReference(sp.x)
                    self.add_spectrum(hdu.header["PIXEL-X"], hdu.header["PIXEL-Y"], sp)
        finally:
            self.enable_update()

    def to_compass_cube(self):
        """Creates CompassCube object"""
        assert len(self.spectra) > 0, "No spectra added"

        ccube = CompassCube()
        wl_new = ccube.wavelength = self.wavelength
        dims = len(wl_new), self.height, self.width
        ccube.create1(self.R, dims, self.hr_pix_size, self.hrfactor)
        for item in self.spectra:
            ii0 = BSearchCeil(wl_new, item.sp.x[0])
            ccube.hdu.data[ii0:ii0+len(item.sp), item.y, item.x] = item.sp.y
        ccube.set_wavelength(self.wavelength)
        return ccube

    def to_colors(self, visible_range=None, flag_scale=False, method=0):
        """Returns a [nY, nX, 3] red-green-blue (0.-1.) matrix

        Arguments:
          visible_range=None -- if passed, the true human visible range will be
                                affine-transformed to visible_range in order
                                to use the red-to-blue scale to paint the pixels
          flag_scale -- whether to scale the luminosities proportionally
                        the weight for each spectra will be the area under the flux
          method -- see Spectrum.get_rgb()
        """
        im = np.zeros((self.height, self.width, 3))
        weights = np.zeros((self.height, self.width, 3))
        max_area = 0.
        for i in range(self.width):
            for j in range(self.height):
                sp = self.get_pixel(i, j, False)
                if len(sp) > 0:
                    im[j, i, :] = sp.get_rgb(visible_range, method)
                    sp_area = np.sum(sp.y)
                    max_area = max(max_area, sp_area)
                    if flag_scale:
                        weights[j, i, :] = sp_area
        if flag_scale:
            weights *= 1./max_area
            im *= weights
        return im

    def to_hdulist(self):
        if len(self.spectra) == 0:
            raise RuntimeError("At the moment, saving file with no spectra is not supported")

        dl = self.reference.delta_lambda

        hdul = fits.HDUList()

        hdu = fits.PrimaryHDU()
        hdu.header["CDELT1"] = self.hr_pix_size
        hdu.header["CDELT2"] = self.hr_pix_size
        hdu.header["CDELT3"] = dl
        hdu.header["CRVAL3"] = self.wavelength[0]-dl
        hdu.header["HRFACTOR"] = self.hrfactor
        hdu.header["R"] = self.R
        hdu.header["TAINHA"] = 26.9752

        hdul.append(hdu)

        for item in self.spectra:
            hdu = fits.PrimaryHDU()
            hdu.header["PIXEL-X"] = item.x
            hdu.header["PIXEL-Y"] = item.y
            hdu.header["CDELT1"] = dl
            hdu.header["CRVAL1"] = item.sp.x[0]  # **note** not subtracting dl as required in WebSimCompass format
            hdu.data = item.sp.y
            hdul.append(hdu)

        return hdul


    def add_spectrum(self, x, y, sp):
        """
        "Paints" pixel with given spectrum

        Arguments:
            x -- x-coordinate
            y -- y-coordinate
            sp -- Spectrum instance

        **Note** coordinate (x=0, y=0) corresponds to lower left pixel of cube cross-section
        """
        assert isinstance(sp, Spectrum)
        # assert self.flag_created, "Cube has not been created yet"
        # assert len(sp.wavelength) == self.hdu.data.shape[0], \
        #     "Spectrum number of points does not match 3rd dimension of cube"

        if len(sp.x) < 2:
            raise RuntimeError("Spectrum must have at least two points")

        self.spectra.append(SkySpectrumItem(x, y, -1, sp))
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

    def get_pixel(self, x, y, flag_copy=True):
        """Creates spectrum on-the-fly containing all spectra merged for pixel (x, y)

        **Note** if there is no spectra at point (x, y), returns an empty spectrum, for speed

        Arguments:
            x, y -- 0-based pixel coordinates
            flag_copy -- disable vector copies to speed up but don't the spectrum
        """

        sp = Spectrum()
        if len(self.spectra) > 0:
            any_ = False
            for item in self.spectra:
                if item.x == x and item.y == y:
                    if not any_:
                        wl_new = sp.x = self.wavelength if not flag_copy else np.copy(self.wavelength)
                        sp.y = np.zeros(len(self.wavelength))
                        any_ = True
                    ii0 = BSearchCeil(wl_new, item.sp.x[0])
                    sp.y[ii0:ii0 + len(item.sp)] = item.sp.y
        return sp

    def __update(self):
        """Updates internal state

        - resamples necessary vectors
        - spectra z-positions
        - wavelength vector
        """

        if not self.__flag_update:
            self.__flag_update_pending = True
            return

        if len(self.spectra) == 0:
            return

        if not self.reference:
            self.reference = _LambdaReference(self.spectra[0].sp.wavelength)

        wlmax = max([item.sp.x[-1] for item in self.spectra])
        wlmin = min([item.sp.x[0] for item in self.spectra])
        dl = self.reference.delta_lambda
        wlmin = (wlmin//dl)*dl
        wlmax = np.ceil(wlmax/dl)*dl
        wl = self.wavelength = np.arange(wlmin, wlmax+dl, dl)

        for item in self.spectra:

            i0 = BSearchCeil(wl, item.sp.x[0])
            assert i0 != -1, "BSearchCeil(wl, item.sp.x[0]) FAILED"
            i1 = BSearchFloor(wl, item.sp.x[-1])
            assert i1 != -1, "BSearchFloor(wl, item.sp.x[-1]) FAILED"

            if item.sp.delta_lambda != dl or wl[i0] != item.sp.x[0] or wl[i1] != item.sp.x[-1]:
                # # Linear interpolation: either adjust for different delta lambda or misaligned wavelengths
                wl_new = wl[i0:i1+1]
                f = interp1d(item.sp.x, item.sp.y)
                sp_new = Spectrum()
                sp_new.x = wl_new
                sp_new.y = f(wl_new)
                # Replaces sp
                item.sp = sp_new

            item.z = i0


class FileSky(DataFile):
    """Represents a Compass data cube file, which is also a FITS file"""
    attrs = ['sky']
    description = "FileSky FITS cube"
    default_filename = "default.sky.fits"

    def __init__(self):
        DataFile.__init__(self)
        self.sky = Sky()

    def _do_load(self, filename):
        fits_obj = fits.open(filename)
        self.sky = Sky()
        self.sky.from_hdulist(fits_obj)
        self.filename = filename

    def _do_save_as(self, filename):
        if os.path.isfile(filename):
            os.unlink(filename)  # PyFITS does not overwrite file
        hdul = self.sky.to_hdulist()
        hdul.writeto(filename)

    def init_default(self):
        # Already created OK
        pass
