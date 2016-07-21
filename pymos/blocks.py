from pyfant import *
from pymos.misc import *
import numpy as np

__all__ = ["Block", "Rubberband"]

class Block(object):
    """Block -- class with a "use" method"""

    def use(self, input):
        # If the output wavelength vector is the same, flag_copy_wavelength determines whether this vector
        # will be copied or just assigned to the output
        #
        # **Attention** blocks that handle the wavelength vectors must comply
        self.flag_copy_wavelength = False
        output = self._do_use(input)
        assert output is not None  # it is common to forger to return in _do_use()
        # Automatically assigns output wavelength vector if applicable
        if isinstance(output, Spectrum) and output.wavelength is None and len(output.y) == len(input.y):
            output.wavelength = np.copy(input.wavelength) if self.flag_copy_wavelength else input.wavelength
        return output

    def _do_use(self, input):
        output = input


class Rubberband(Block):
    """Returns a rubber band"""
    def _do_use(self, input):
        output = Spectrum()
        output.y = rubberband(input.y)
        return output