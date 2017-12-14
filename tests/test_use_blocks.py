import aosss
import numpy as np
import f311


def get_spectrum():
    sp = f311.Spectrum()
    sp.x = np.linspace(5000, 5100, 100)
    sp.y = np.random.random(100)+2.
    sp.filename = "random"
    return sp

def get_spectrum_list():
    sl = aosss.SpectrumList()
    for i in range(3):
        sl.add_spectrum(get_spectrum())
    return sl


def test_use_GB_SNR():
    sl = get_spectrum_list()
    blk = aosss.GB_SNR()
    out = blk.use(sl)


def test_use_GB_UseNumPyFunc():
    sl = get_spectrum_list()
    blk = aosss.GB_UseNumPyFunc(np.sum)
    out = blk.use(sl)


def test_use_SB_Add():
    sp = get_spectrum()
    blk = aosss.SB_Add(2.)
    out = blk.use(sp)


def test_use_SB_AddNoise():
    sp = get_spectrum()
    blk = aosss.SB_AddNoise()
    out = blk.use(sp)


def test_use_SB_ConvertYUnit():
    sp = get_spectrum()
    blk = aosss.SB_ConvertYUnit(f311.flambda)
    out = blk.use(sp)


def test_use_SB_Cut():
    sp = get_spectrum()
    blk = aosss.SB_Cut(5000, 5050)
    out = blk.use(sp)


def test_use_SB_DivByLambda():
    sp = get_spectrum()
    blk = aosss.SB_DivByLambda()
    out = blk.use(sp)


def test_use_SB_ElementWise():
    sp = get_spectrum()
    blk = aosss.SB_ElementWise(lambda x: x+1)
    out = blk.use(sp)


def test_use_SB_Extend():
    sp = get_spectrum()
    blk = aosss.SB_Extend()
    out = blk.use(sp)


def test_use_SB_FLambdaToFNu():
    sp = get_spectrum()
    blk = aosss.SB_FLambdaToFNu()
    out = blk.use(sp)


def test_use_SB_FNuToFLambda():
    sp = get_spectrum()
    blk = aosss.SB_FNuToFLambda()
    out = blk.use(sp)


def test_use_SB_Mul():
    sp = get_spectrum()
    blk = aosss.SB_Mul(2.)
    out = blk.use(sp)


def test_use_SB_MulByLambda():
    sp = get_spectrum()
    blk = aosss.SB_MulByLambda()
    out = blk.use(sp)


def test_use_SB_Normalize():
    sp = get_spectrum()
    blk = aosss.SB_Normalize()
    out = blk.use(sp)


def test_use_SB_Rubberband():
    sp = get_spectrum()
    blk = aosss.SB_Rubberband()
    out = blk.use(sp)


def test_use_SLB_ExtractContinua():
    sl = get_spectrum_list()
    blk = aosss.SLB_ExtractContinua()
    out = blk.use(sl)


def test_use_SLB_UseSpectrumBlock():
    sl = get_spectrum_list()
    blk = aosss.SLB_UseSpectrumBlock(aosss.SB_Rubberband())
    out = blk.use(sl)


def test_use_ToScalar_Magnitude():
    sp = get_spectrum()
    blk = aosss.ToScalar_Magnitude("B")
    out = blk.use(sp)


def test_use_ToScalar_SNR():
    sp = get_spectrum()
    blk = aosss.ToScalar_SNR(5000,5100)
    out = blk.use(sp)


def test_use_ToScalar_UseNumPyFunc():
    sp = get_spectrum()
    blk = aosss.ToScalar_UseNumPyFunc(np.sum)
    out = blk.use(sp)

