import astroapi as aa
import aosss as ao


__all__ = ["get_aosss_path", "get_aosss_data_path", "get_aosss_scripts_path", ]


def get_aosss_path(*args):
  """Returns full path aosss package. Arguments are added at the end of os.path.join()"""
  return aa.get_path(*args, module=ao)
  # p = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), *args))
  # return p


def get_aosss_data_path(*args):
    """Returns path to aosss scripts. Arguments are added to the end os os.path.join()"""
    return get_aosss_path("data", *args)


def get_aosss_scripts_path(*args):
    """Returns path to aosss scripts. Arguments are added to the end os os.path.join()"""
    return get_aosss_path("..", "scripts", *args)


def load_eso_sky():
    """Loads ESO sky model and returns two spectra: emission, transmission"""

    # From comments in file:
    # lam:     vacuum wavelength in micron
    # flux:    sky emission radiance flux in ph/s/m2/micron/arcsec2
    # dflux1:  sky emission -1sigma flux uncertainty
    # dflux2:  sky emission +1sigma flux uncertainty
    # dtrans:  sky transmission
    # dtrans1: sky transmission -1sigma uncertainty
    # dtrans2: sky transmission +1sigma uncertainty


    path_ = get_aosss_data_path()

    hl = fits.open(os.path.join(path_, "eso-sky.fits"))
    d = hl[1].data

    x, y0, y1 = d["lam"]*10000, d["flux"], d["trans"]

    sp0 = aa.Spectrum()
    sp0.x, sp0.y = x, y0
    sp0.yunit = u.Unit("ph/s/m2/angstrom/arcsec2")

    sp1 = aa.Spectrum()
    sp1.x, sp1.y = x, y1

    return sp0, sp1