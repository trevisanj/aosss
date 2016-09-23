__all__ = ["load_spectrum_from_fits_cube_or_not", "load_bulk"]

import numpy as np
from pyfant import *
from astropy.io import fits
import os.path
from collections import OrderedDict
from filepar import *


def load_spectrum_from_fits_cube_or_not(filename, x=0, y=0):
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


FILE_MAP = OrderedDict((
 ("cube_hr", FileWebsimCube),
 ("cube_seeing", FileFits),
 ("ifu_noseeing", FileWebsimCube),
 ("mask_fiber_in_aperture", FileFits),  # TODO, handle this file because it is nice
 ("reduced", FileWebsimCube),
 ("reduced_snr", FileWebsimCube),
 ("sky", FileSpectrumFits),
 ("skysub", FileSpectrumFits),
 ("spintg", FileSpectrumFits),
 ("spintg_noseeing", "messed"),  # particular case
 ("therm", "messed"),            # particular case
 ("PAR", FilePar)             # particular case
))
#
# FILE_KEYWORDS = FILE_MAP.keys()


class BulkItem(object):
    """This is each item returned by load_bulk"""
    def __init__(self, keyword=None, fileobj=None, filename=None, flag_exists=None,
                 flag_supported=None, error=None):
        # fileobj may be a DataFile or a string (the latter if the .par file)
        self.keyword = keyword
        self.fileobj = fileobj
        self.filename = filename
        self.flag_exists = flag_exists
        self.flag_supported = flag_supported
        self.error = error


def load_bulk(simid, dir_='.'):
    """
    Loads all files given the simulation id. Returns an list of BulkItem

    The keys are the same as in FILE_KEYWORDS, in the same order as well
    """

    ret = []
    sp_ref = None  # reference spectrum for x-axis of messed files
    for keyword, class_ in FILE_MAP.iteritems():
        if keyword == "PAR":
            fn = simid+".par"
        else:
            fn = os.path.join(dir_, "%s_%s.fits" % (simid, keyword))
        flag_exists = os.path.isfile(fn)
        flag_supported = class_ is not None
        error = None
        fileobj = None
        if flag_exists:
            if class_ == "messed":
                # Note that sp_ref may be None here if Cxxxx_spintg.fits fails to load
                # In this case, sp will have a default x-axis
                sp = load_spectrum_fits_messed_x(fn, sp_ref)
                if sp:
                    fileobj = FileSpectrum()
                    fileobj.spectrum = sp
            elif flag_supported:
                fileobj = class_()
                try:
                    fileobj.load(fn)
                except Exception as E:
                    get_python_logger().exception("Error loading file '%s'" % fn)
                    error = str(E)

                if keyword == "spintg":
                    # Saves reference spectrum to use its x-axis to complete
                    # the "messed" files
                    sp_ref = fileobj.spectrum

            ret.append(BulkItem(keyword, fileobj, fn, flag_exists, flag_supported,
                            error))
    return ret