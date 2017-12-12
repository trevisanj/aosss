import os
import f311.filetypes as ft



def test_FileSparseCube(tmpdir):
    os.chdir(str(tmpdir))
    obj = ft.FileSparseCube()
    obj.init_default()
    obj.save_as()


def test_FileSpectrumList(tmpdir):
    os.chdir(str(tmpdir))
    obj = ft.FileSpectrumList()
    obj.init_default()
    obj.save_as()


