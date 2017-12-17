import aosss.physics as ph
import matplotlib.pyplot as plt
import numpy as np


l0, lf = 3000, 250000
x =  np.logspace(np.log10(l0), np.log10(lf), 1000, base=10.)

ax = plt.subplot(211)
for name in "UBVRI":
    bp = ph.UBVTabulated(name)
    plt.semilogx(x, bp.ufunc()(x), label=name)
plt.xlim([l0, lf])
plt.title("Tabulated")

plt.subplot(212, sharex=ax)
for name in "UBVRIYJHKLMNQ":
    bp = ph.UBVParametric(name)
    plt.semilogx(x, bp.ufunc()(x), label=name)
plt.xlim([l0, lf])
plt.xlabel("Wavelength ($\AA$)")
plt.title("Parametric")
l = plt.legend(loc='lower right')

plt.tight_layout()
plt.show()