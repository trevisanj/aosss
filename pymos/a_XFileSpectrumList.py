"""Window to edit both main and abundances"""

__all__ = ["XFileSpectrumList"]

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from a_WFileSpectrumList import *
from pyfant import *
from pyfant.gui.guiaux import *
from pyfant.gui import XRunnableManager  # Everything related to XRunnableManager stays as a template for a future optimization manager
from pyfant import *
import os
import os.path
import re
import matplotlib.pyplot as plt
from filesky import *
from fileccube import *
from filespectrumlist import *
from pyfant.gui.a_XParametersEditor import *
from basewindows import *

VVV = FileSpectrumList.description


################################################################################
class XFileSpectrumList(XLogMainWindow):
    def __init__(self, parent=None):
        XLogMainWindow.__init__(self, parent)

        self.__refs = []
        def keep_ref(obj):
            self.__refs.append(obj)
            return obj

        # # Synchronized sequences
        self.tab_texts[0] =  "FileSpectrumList editor (Alt+&1)"
        self.tabWidget.setTabText(0, self.tab_texts[0])
        self.save_as_texts[0] = "Save %s as..." % VVV
        self.open_texts[0] = "Load %s" % VVV
        self.clss[0] = FileSpectrumList
        self.clsss[0] = (FileSpectrumList, FileCCube)  # file types that can be opened
        self.wilds[0] = "*.fits"

        lv = keep_ref(QVBoxLayout(self.gotting))
        ce = self.ce = WFileSpectrumList(self)
        lv.addWidget(ce)
        ce.edited.connect(self.on_tab0_file_edited)
        self.editors[0] = ce

        # # Loads default file by default
        if os.path.isfile(FileSpectrumList.default_filename):
            f = FileSpectrumList()
            f.load()
            self.ce.load(f)

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # Interface

    def set_manager_form(self, x):
        assert isinstance(x, XRunnableManager)
        self._manager_form = x
        self._rm = x.rm

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # Qt override

    def closeEvent(self, event):
        flag_exit, ff = True, []
        for ed, flag_changed in zip(self.editors, self.flags_changed):
            if ed and ed.f and flag_changed:
                ff.append(ed.f.description)

        if len(ff) > 0:
            s = "Unsaved changes\n  -"+("\n  -".join(ff))+"\n\nAre you sure you want to exit?"
            flag_exit = are_you_sure(True, event, self, "Unsaved changes", s)
        if flag_exit:
            plt.close("all")

    def keyPressEvent(self, evt):
        incr = 0
        if evt.modifiers() == Qt.ControlModifier:
            n = self.tabWidget.count()
            if evt.key() in [Qt.Key_PageUp, Qt.Key_Backtab]:
                incr = -1
            elif evt.key() in [Qt.Key_PageDown, Qt.Key_Tab]:
                incr = 1
            if incr != 0:
                new_index = self._get_tab_index() + incr
                if new_index < 0:
                    new_index = n-1
                elif new_index >= n:
                    new_index = 0
                self.tabWidget.setCurrentIndex(new_index)

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # Slots for Qt library signals

    # def on_show_rm(self):
    #     if self._manager_form:
    #         self._manager_form.show()
    #         self._manager_form.raise_()
    #         self._manager_form.activateWindow()


    def on_tab0_file_edited(self):
        self._on_edited()

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # Protected methods to be overriden or used by descendant classes

    def _on_edited(self):
        index = self._get_tab_index()
        self.flags_changed[index] = True
        self._update_tab_texts()

    def _filter_on_load(self, f):
        """Converts from FileCCube to FileSpectrumList format, if necessary"""
        if isinstance(f, FileCCube):
            f1 = FileSpectrumList()
            f1.sky.from_compass_cube(f.ccube)
            f = f1
        return f
