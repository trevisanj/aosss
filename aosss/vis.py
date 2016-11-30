from astroapi import Vis
from aosss.datatypes import *


class VisCube(Vis):
    """Opens the Data Cube Editor window."""
    input_classes = (FileFullCube, FileSparseCube)
    action = "Edit using Data Cube Editor"

    def _do_use(self, r):
        from pyfant.gui.aosss import XFileSparseCube
        form = XFileSparseCube(self.parent_form, r)
        _forms.append(form)
        form.show()


class VisSpectrumList(Vis):
    """Opens the Spectrum List Editor window."""
    input_classes = (FileSpectrumList, FileSpectrum)
    action = "Edit using Spectrum List Editor"

    def _do_use(self, r):
        from pyfant.gui.aosss import XFileSpectrumList
        form = XFileSpectrumList(self.parent_form, r)
        _forms.append(form)
        form.show()
