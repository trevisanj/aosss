import aosss as ao
import astrogear as ag


def test_WFileSparseCube():
    app = ag.get_QApplication()
    obj = ao.WFileSparseCube(ag.XLogMainWindow())


def test_WFileSpectrumList():
    app = ag.get_QApplication()
    obj = ao.WFileSpectrumList(ag.XLogMainWindow())


def test_WSpectrumCollection():
    app = ag.get_QApplication()
    obj = ao.WSpectrumCollection(ag.XLogMainWindow())


def test_XFileSparseCube():
    app = ag.get_QApplication()
    obj = ao.XFileSparseCube()


def test_XFileSpectrumList():
    app = ag.get_QApplication()
    obj = ao.XFileSpectrumList()


def test_XGroupSpectra():
    app = ag.get_QApplication()
    obj = ao.XGroupSpectra()


def test_XHelpDialog():
    app = ag.get_QApplication()
    obj = ao.XHelpDialog()


def test_XPlotXY():
    app = ag.get_QApplication()
    obj = ao.XPlotXY(ao.SpectrumCollection())


def test_XPlotXYZ():
    app = ag.get_QApplication()
    obj = ao.XPlotXYZ(ao.SpectrumCollection())


def test_XScaleSpectrum():
    app = ag.get_QApplication()
    obj = ao.XScaleSpectrum()


def test_XToScalar():
    app = ag.get_QApplication()
    obj = ao.XToScalar()


def test_XUseSpectrumBlock():
    app = ag.get_QApplication()
    obj = ao.XUseSpectrumBlock()

