import aosss
import os



def test_FileSparseCube(tmpdir):
    os.chdir(str(tmpdir))
    obj = aosss.FileSparseCube()
    obj.init_default()
    obj.save_as()


def test_FileSpectrumList(tmpdir):
    os.chdir(str(tmpdir))
    obj = aosss.FileSpectrumList()
    obj.init_default()
    obj.save_as()


