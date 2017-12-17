import aosss
import f311
import numpy as np

def test_get_rgb():
    sp = f311.Spectrum()
    N = 100
    sp.y = np.ones((N,))
    sp.x = np.linspace(4000, 7000, N)

    rgb = aosss.get_rgb(sp, method=1)

    assert all(rgb == 1)