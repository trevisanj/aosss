import a99
import f311
import aosss


__all__ = ["VisCube", "VisSpectrumList"]


class VisCube(f311.Vis):
    """Opens the Data Cube Editor window."""
    input_classes = (aosss.FileFullCube, aosss.FileSparseCube)
    action = "Edit using Data Cube Editor"

    def _do_use(self, r):
        form = a99.keep_ref(aosss.XFileSparseCube(self.parent_form, r))
        form.show()


class VisSpectrumList(f311.Vis):
    """Opens the Spectrum List Editor window."""
    input_classes = (aosss.FileSpectrumList, f311.FileSpectrum)
    action = "Edit using Spectrum List Editor"

    def _do_use(self, r):
        form = a99.keep_ref(aosss.XFileSpectrumList(self.parent_form, r))
        form.show()
