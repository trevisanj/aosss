import aosss
from astropy import units as u

def test_GB_SNR():
    _ = aosss.GB_SNR()


def test_GB_UseNumPyFunc():
    _ = aosss.GB_UseNumPyFunc()


def test_GroupBlock():
    _ = aosss.GroupBlock()


def test_SB_Add():
    _ = aosss.SB_Add()


def test_SB_AddNoise():
    _ = aosss.SB_AddNoise()


def test_SB_ConvertYUnit():
    _ = aosss.SB_ConvertYUnit(u.Jy)


def test_SB_Cut():
    _ = aosss.SB_Cut(5000, 6000)


def test_SB_DivByLambda():
    _ = aosss.SB_DivByLambda()


def test_SB_ElementWise():
    _ = aosss.SB_ElementWise(lambda x: x-1)


def test_SB_Extend():
    _ = aosss.SB_Extend()


def test_SB_FLambdaToFNu():
    _ = aosss.SB_FLambdaToFNu()


def test_SB_FNuToFLambda():
    _ = aosss.SB_FNuToFLambda()


def test_SB_Mul():
    _ = aosss.SB_Mul()


def test_SB_MulByLambda():
    _ = aosss.SB_MulByLambda()


def test_SB_Normalize():
    _ = aosss.SB_Normalize()


def test_SB_Rubberband():
    _ = aosss.SB_Rubberband()


def test_SLB_ExtractContinua():
    _ = aosss.SLB_ExtractContinua()


def test_SLB_UseSpectrumBlock():
    _ = aosss.SLB_UseSpectrumBlock()


def test_SpectrumBlock():
    _ = aosss.SpectrumBlock()


def test_SpectrumListBlock():
    _ = aosss.SpectrumListBlock()


def test_ToScalar():
    _ = aosss.ToScalar()


def test_ToScalar_Magnitude():
    _ = aosss.ToScalar_Magnitude("U")


def test_ToScalar_SNR():
    _ = aosss.ToScalar_SNR(0, 100000)


def test_ToScalar_UseNumPyFunc():
    _ = aosss.ToScalar_UseNumPyFunc()

