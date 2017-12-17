# Plots blackbody curves (normalized to max=1.0) for red, yellow and blue stars;
# Calculates colors for these stars
#
# Adapted from https://stackoverflow.com/questions/22417484/plancks-formula-for-blackbody-spectrum

import matplotlib.pyplot as plt
import numpy as np
import aosss.physics as ph
import f311

# color, temperature (K)
stars = [("blue", 10000),
         ("yellow", 5700),
         ("red", 4000),
         ("very red", 3000),
         ]

h = 6.626e-34
c = 3.0e+8
k = 1.38e-23

def planck(wav, T):
    """wav in angstrom, T in kelvin"""

    wav_ = wav*1e-10 # converts to m

    a = 2.0*h*c**2
    b = h*c/(wav_ * k * T)
    intensity = a/ ((wav_ ** 5) * (np.exp(b) - 1.0))
    return intensity

# x-axis wavelength in angstrom
wavelengths = np.linspace(10., 30000., 1000)

plt.style.use("dark_background")
for name, temperature in stars:
    flux = planck(wavelengths, temperature)
    flux /= np.max(flux)
    color = ph.get_rgb(f311.Spectrum(wavelengths, flux), method=1)
    plt.plot(wavelengths, flux, color=color, label="{} star ({} K)".format(name, temperature))

plt.legend(loc=0)
plt.xlabel("Wavelength (angstrom)")
plt.ylabel("Flux (a.u.)")
plt.title("Normalized blackbody curves")
plt.tight_layout()
plt.show()