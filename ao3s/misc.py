__all__ = ["get_ao3s_path", "get_ao3s_data_path", "get_ao3s_scripts_path",
"load_spectrum_from_fits_cube_or_not", "FILE_MAP", "BulkItem", "load_bulk", "create_spectrum_lists"]


from astropy.io import fits
import os.path
from collections import OrderedDict
import glob
import os
import re
import numpy as np
from pyfant import *


def get_ao3s_path(*args):
  """Returns full path ao3s package. Arguments are added at the end of os.path.join()"""
  p = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), *args))
  return p


def get_ao3s_data_path(*args):
    """Returns path to ao3s scripts. Arguments are added to the end os os.path.join()"""
    return get_ao3s_path("data", *args)


def get_ao3s_scripts_path(*args):
    """Returns path to ao3s scripts. Arguments are added to the end os os.path.join()"""
    return get_ao3s_path("..", "scripts", *args)


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
 ("cube_hr", FileFullCube),
 ("cube_seeing", FileFits),
 ("ifu_noseeing", FileFullCube),
 ("mask_fiber_in_aperture", FileFits),  # TODO, handle this file because it is nice
 ("reduced", FileFullCube),
 ("reduced_snr", FileFullCube),
 ("sky", FileSpectrumFits),
 ("skysub", FileSpectrumFits),
 ("spintg", FileSpectrumFits),
 ("spintg_noseeing", "messed"),  # particular case
 ("therm", "messed"),            # particular case
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


def create_spectrum_lists(dir_):
    """Create several .splist files, grouping spectra by their wavelength vector"""

    fnfn = glob.glob(os.path.join(dir_, "C*.par"))
    # # Loads everything that's needed from disk
    fileobjs = []  # (FilePar, FileSpectrumFits) pairs
    for fn in fnfn:
        try:
            gg = re.search('C(\d+)', fn)
            if gg is None:
                raise RuntimeError(
                    "'.par' file name '%s' does not have pattern 'Cnnnnnn'" % fn)

            fp = FilePar()
            fp.load(fn)

            spectrum_filename = os.path.join(dir_, gg.group() + "_spintg.fits")
            fsp = FileSpectrumFits()
            fsp.load(spectrum_filename)

            fileobjs.append((fp, fsp))
        except:
            get_python_logger().exception(
                "Failed to add spectrum corresponding to file '%s'" % fn)

    # Groups files by their wavelength axis
    groups = []  # list of lists: [[(FilePar0, FileSpectrumFits0), ...], ...]
    for pair in fileobjs:
        if len(groups) == 0:
            groups.append([pair])
        else:
            flag_match = False
            for group in groups:
                wl0 = group[0][1].spectrum.wavelength
                wl1 = pair[1].spectrum.wavelength
                if len(wl0) == len(wl1) and np.all(wl0 == wl1):
                    flag_match = True
                    group.append(pair)
                    break
            if not flag_match:
                groups.append([pair])

    # Now creates the spectrum list files
    for h, group in enumerate(groups):

        # # Finds differences in simulation specifications
        # Finds names of parameters that differ at least in one file using set operations
        for i, (fp, _) in enumerate(group):
            s = set(fp.params.items())
            if i == 0:
                s_union = s
                s_overlap = s
            else:
                s_union = s_union | s
                s_overlap = s_overlap & s
        keys = dict(s_union - s_overlap).keys()
        key_dict = make_fits_keys_dict(keys)

        # get_python_logger().info("FITS headers to feature in all spectra:")
        # get_python_logger().info(str(key_dict))


        fspl = FileSpectrumList()
        nmin, nmax = 9999999, 0
        for fp, fsp in group:
            try:
                gg = re.search('C(\d+)', fp.filename)
                if gg is None:
                    raise RuntimeError(
                        "'.par' file name '%s' does not have pattern 'Cnnnnnn'" % fp.filename)
                n = int(gg.groups()[0])
                nmin = min(n, nmin)
                nmax = max(n, nmax)

                sp = fsp.spectrum
                # gets rid of all FITS headers (TODO not sure if this is a good idea yet)
                sp.more_headers.clear()
                sp.more_headers["ORIGIN"] = os.path.basename(fsp.filename)

                # copies to spectrum header all key-value pairs that differ among .par files
                for k in keys:

                    # unwanted parameters
                    # - simu name is redundant with simu_id
                    # - ext_link has info such as "Resource id #4"
                    if k in ["ext_link", "simu_name"]:
                        # TODO not efficient to have this here, should remove from keys
                        continue

                    value = fp.params.get(k)
                    if value is not None:
                        # Content-sensitive conversion
                        if k == "obj_ftemplate":
                            # Template filename comes with full local
                            # (i.e. Websim server) path, which is unnecessary
                            # for our identification
                            value = os.path.basename(value)
                        elif k == "psf_file":
                            # PSF filename also comes with its full path,
                            # which if probably irrelevant
                            value = os.path.basename(value)
                        # else:
                        #       # .get(k)

                    sp.more_headers[key_dict[k]] = value
                    # print "OLHOLHOLHO"

                fspl.splist.add_spectrum(sp)
            except:
                get_python_logger().exception(
                    "Failed to add spectrum corresponding to file '%s'" % fp.filename)

        fn = os.path.join(dir_, "%sC%06d-C%06d.splist" % (
            ("group%d-" % h) if len(groups) > 0 else "", nmin, nmax))
        fspl.save_as(fn)
        get_python_logger().info("Created file '%s'" % fn)


