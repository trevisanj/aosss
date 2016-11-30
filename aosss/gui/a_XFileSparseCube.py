__all__ = ["XFileSparseCube"]

import collections
import copy
import matplotlib.pyplot as plt
from pylab import MaxNLocator
import numbers
import numpy as np
import os
import os.path
from itertools import product, combinations, cycle
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from astrotypes import *
from pyfant.datatypes.filesplist import *
from pyfant.gui import *
from .basewindows import *
from .a_WChooseSpectrum import *
from .a_XScaleSpectrum import *
from .a_WFileSparseCube import *

class XFileSparseCube(XFileMainWindow):
    def __init__(self, parent=None, fileobj=None):
        XFileMainWindow.__init__(self, parent)

        def keep_ref(obj):
            self._refs.append(obj)
            return obj

        self.setWindowTitle(get_window_title("Data Cube Editor"))


        # # Synchronized sequences
        _VVV = FileSparseCube.description
        self.tab_texts[0] =  "FileSparseCube editor (Alt+&1)"
        self.tabWidget.setTabText(0, self.tab_texts[0])
        self.save_as_texts[0] = "Save %s as..." % _VVV
        self.open_texts[0] = "Load %s" % _VVV
        self.clss[0] = FileSparseCube
        self.clsss[0] = (FileSparseCube, FileFullCube)  # file types that can be opened
        self.wilds[0] = "*.fits"

        lv = keep_ref(QVBoxLayout(self.gotting))
        ce = self.ce = WFileSparseCube(self)
        lv.addWidget(ce)
        ce.edited.connect(self.on_tab0_file_edited)
        self.editors[0] = ce

        # # # Loads default file by default ... SQN
        # if os.path.isfile(FileSparseCube.default_filename):
        #     f = FileSparseCube()
        #     f.load()
        #     self.ce.load(f)

        if fileobj is not None:
            self.load(fileobj)


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
        """Converts from FileFullCube to FileSparseCube format, if necessary"""
        f1 = None
        if isinstance(f, FileFullCube):
            f1 = FileSparseCube()
            f1.sparsecube.from_full_cube(f.wcube)
        if f1:
            f1.filename = add_bits_to_path(f.filename, "imported-from-",
                                           os.path.splitext(FileSparseCube.default_filename)[1])
            f = f1
        return f
