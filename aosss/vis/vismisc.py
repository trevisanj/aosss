import hypydrive as hpd
from hypydrive import Vis
import aosss as ao


__all__ = ["VisCube", "VisSpectrumList"]


class VisCube(Vis):
    """Opens the Data Cube Editor window."""
    input_classes = (ao.FileFullCube, ao.FileSparseCube)
    action = "Edit using Data Cube Editor"

    def _do_use(self, r):
        form = hpd.keep_ref(ao.XFileSparseCube(self.parent_form, r))
        form.show()


class VisSpectrumList(Vis):
    """Opens the Spectrum List Editor window."""
    input_classes = (ao.FileSpectrumList, hpd.FileSpectrum)
    action = "Edit using Spectrum List Editor"

    def _do_use(self, r):
        form = hpd.keep_ref(ao.XFileSpectrumList(self.parent_form, r))
        form.show()
