""""
List of spectra sharing same wavenumber axis. Uses FITS format
"""

__all__ = ["FileSpectrumList"]


from . import SpectrumList
from hypydrive import DataFile, froze_it, overwrite_fits
from astropy.io import fits


@froze_it
class FileSpectrumList(DataFile):
    """FITS Spectrum List"""
    attrs = ['splist']
    description = "Spectrum List"
    default_filename = "default.splist"

    def __init__(self):
        DataFile.__init__(self)
        self.splist = SpectrumList()

    def _do_load(self, filename):
        fits_obj = fits.open(filename)
        self.splist = SpectrumList()
        self.splist.from_hdulist(fits_obj)
        self.filename = filename

    def _do_save_as(self, filename):
        hdul = self.splist.to_hdulist()
        overwrite_fits(hdul, filename)

    def init_default(self):
        # Already created OK
        pass
