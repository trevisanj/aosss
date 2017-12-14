__all__ = ["XFileSpectrumList"]


from .a_WFileSpectrumList import *
import aosss
import a99
import f311


class XFileSpectrumList(f311.XFileMainWindow):
    def _add_stuff(self):
        self.setWindowTitle(a99.get_window_title("Spectrum List Editor"))

        ce = self.ce = WFileSpectrumList(self)

        self.pages.append(f311.MyPage(text_tab="FileSpectrumList editor", cls_save=aosss.FileSpectrumList,
            clss_load=[aosss.FileSpectrumList, aosss.FileFullCube]+f311.classes_sp(), wild="*.splist",
            editor=ce))

        # # Adds spectrum collection actions to menu
        self.menuBar().addMenu(self.ce.menu_actions)
