"""
Rainbow colors

Example:

>>> for color in rainbow_colors:
...     color
Color('Violet', [ 0.54509804  0.          1.        ], 4000.0, 3775.0, 4225.0)
Color('Indigo', [ 0.29411765  0.          0.50980392], 4450.0, 4225.0, 4600.0)
Color('Blue', [ 0.  0.  1.], 4750.0, 4600.0, 4925.0)
Color('Green', [ 0.  1.  0.], 5100.0, 4925.0, 5400.0)
Color('Yellow', [ 1.  1.  0.], 5700.0, 5400.0, 5800.0)
Color('Orange', [ 1.          0.49803922  0.        ], 5900.0, 5800.0, 6200.0)
Color('Red', [ 1.  0.  0.], 6500.0, 6200.0, 6800.0)

Example:

>>> import aosss
>>> import matplotlib.pyplot as plt
>>> for color in aosss.rainbow_colors:
...     _ = plt.fill_between([color.l0, color.lf], [1., 1.], color=color.rgb, label=color.name)
>>> _ = plt.legend(loc=0)
>>> _ = plt.xlabel('Wavelength (angstrom)')
>>> _ = plt.tight_layout()
>>> _ = plt.show()

"""


__all__ = ["Color", "rainbow_colors", "ncolors"]


from a99 import AttrsPart
import numpy as np


class Color(AttrsPart):
    """Definition of a color: name, RGB code, wavelength range"""

    attrs = ["name", "rgb", "clambda", "l0", "lf"]

    def __init__(self, name, rgb, clambda, l0=-1, lf=-1):
        AttrsPart.__init__(self)
        # Name of color
        self.name = name
        # (red, green, blue) tuple (numbers in [0, 1] interval)
        self.rgb = rgb
        # Central wavelength (angstrom)
        self.clambda = clambda
        # Initial wavelength (angstrom)
        self.l0 = l0
        # Final wavelength (angstrom)
        self.lf = lf

    def __repr__(self):
        return "Color('{}', {}, {}, {}, {})".format(self.name, self.rgb, self.clambda, self.l0, self.lf)


#: Rainbow colors
rainbow_colors = [Color("Violet", [139, 0, 255], 4000),
                  Color("Indigo", [75, 0, 130], 4450),
                  Color("Blue", [0, 0, 255], 4750),
                  Color("Green", [0, 255, 0], 5100),
                  Color("Yellow", [255, 255, 0], 5700),
                  Color("Orange", [255, 127, 0], 5900),
                  Color("Red", [255, 0, 0], 6500),
                  ]

# Calculates l0, lf
# rainbow_colors[0].l0 = 0.
# rainbow_colors[-1].lf = float("inf")
for c in rainbow_colors:
    c.clambda = float(c.clambda)
ncolors = len(rainbow_colors)
for i in range(1, ncolors):
    cprev, cnow = rainbow_colors[i-1], rainbow_colors[i]
    avg = (cprev.clambda + cnow.clambda) / 2
    cprev.lf = avg
    cnow.l0 = avg

    if i == 1:
        cprev.l0 = 2*cprev.clambda-cprev.lf
    if i == ncolors-1:
        cnow.lf = 2*cnow.clambda-cnow.l0
# converts RGB from [0, 255] to [0, 1.] interval
for c in rainbow_colors:
    c.rgb = np.array([float(x)/255 for x in c.rgb])
