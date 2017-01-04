import astrogear as ag
from astrogear import Vis
import aosss as ao


__all__ = ["VisCube", "VisSpectrumList"]


class VisCube(Vis):
    """Opens the Data Cube Editor window."""
    input_classes = (ao.FileFullCube, ao.FileSparseCube)
    action = "Edit using Data Cube Editor"

    def _do_use(self, r):
        form = ag.keep_ref(ao.XFileSparseCube(self.parent_form, r))
        form.show()


class VisSpectrumList(Vis):
    """Opens the Spectrum List Editor window."""
    input_classes = (ao.FileSpectrumList, ag.FileSpectrum)
    action = "Edit using Spectrum List Editor"

    def _do_use(self, r):
        form = ag.keep_ref(ao.XFileSpectrumList(self.parent_form, r))
        form.show()
