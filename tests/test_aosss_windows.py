import aosss as ao
import hypydrive as hpd


def test_WFileSparseCube():
    app = hpd.get_QApplication()
    obj = ao.WFileSparseCube(hpd.XLogMainWindow())


def test_WFileSpectrumList():
    app = hpd.get_QApplication()
    obj = ao.WFileSpectrumList(hpd.XLogMainWindow())


def test_WSpectrumCollection():
    app = hpd.get_QApplication()
    obj = ao.WSpectrumCollection(hpd.XLogMainWindow())


def test_XFileSparseCube():
    app = hpd.get_QApplication()
    obj = ao.XFileSparseCube()


def test_XFileSpectrumList():
    app = hpd.get_QApplication()
    obj = ao.XFileSpectrumList()


def test_XGroupSpectra():
    app = hpd.get_QApplication()
    obj = ao.XGroupSpectra()


def test_XHelpDialog():
    app = hpd.get_QApplication()
    obj = ao.XHelpDialog()


def test_XPlotXY():
    app = hpd.get_QApplication()
    obj = ao.XPlotXY(ao.SpectrumCollection())


def test_XPlotXYZ():
    app = hpd.get_QApplication()
    obj = ao.XPlotXYZ(ao.SpectrumCollection())


def test_XScaleSpectrum():
    app = hpd.get_QApplication()
    obj = ao.XScaleSpectrum()


def test_XToScalar():
    app = hpd.get_QApplication()
    obj = ao.XToScalar()


def test_XUseSpectrumBlock():
    app = hpd.get_QApplication()
    obj = ao.XUseSpectrumBlock()

