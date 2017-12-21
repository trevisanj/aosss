import aosss
import f311
import numpy as np

def test_spectrum_to_rgb():
    sp = f311.Spectrum()
    N = 100
    sp.y = np.ones((N,))
    sp.x = np.linspace(4000, 7000, N)

    rgb = aosss.spectrum_to_rgb(sp, method=1)

    assert all(rgb == 1)