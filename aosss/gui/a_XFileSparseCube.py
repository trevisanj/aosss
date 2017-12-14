__ll__ = ["XFileSparseCube"]

from .a_WFileSparseCube import *
import a99
import aosss
import f311

class XFileSparseCube(f311.XFileMainWindow):

    def _add_stuff(self):
        self.setWindowTitle(a99.get_window_title("Data Cube Editor"))

        ce = self.ce = WFileSparseCube(self)

        self.pages.append(f311.MyPage(text_tab="FileSparseCube editor",
         cls_save=aosss.FileSparseCube, clss_load=(aosss.FileSparseCube, aosss.FileFullCube), wild="*.fits", editor=ce))

