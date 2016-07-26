"""Widget to select a UBVRI wavelength band."""

__all__ = ["WBand"]

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from pyfant.gui import *
from pyfant import *
import random
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT # as NavigationToolbar2QT
import matplotlib.pyplot as plt
import numpy as np
from itertools import product, combinations, cycle
import os
import math
import numbers
import copy
import datetime
import traceback as tb
from pymos import *
import scipy

_COLORS_SQ = [(.1, .6, .5), (.5, .1, .7)]
_ITER_COLORS_SQ = cycle(_COLORS_SQ)


class WBand(WBase):
    """
    UBVRI band selector
    """

    edited = pyqtSignal()

    def __init__(self, parent=None):
        WBase.__init__(self, parent)

        def keep_ref(obj):
            self.__refs.append(obj)
            return obj

        self.__refs = []
        # Whether all the values in the fields are valid or not
        self.flag_valid = False
        # Internal flag to prevent taking action when some field is updated programatically
        self.flag_process_changes = False

        self.setFont(MONO_FONT)

        # # Central layout

        lantanide = self.centralLayout = QVBoxLayout()
        lantanide.setMargin(0)
        self.setLayout(lantanide)

        ###
        lg = keep_ref(QGridLayout())
        lantanide.addLayout(lg)
        lg.setMargin(0)
        lg.setVerticalSpacing(4)
        lg.setHorizontalSpacing(5)
        # lscrw.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # field map: [(label widget, edit widget, field name, short description, long description), ...]
        pp = self._map0 = []
        ###
        x = keep_ref(QLabel())
        y = self.cb_band = QComboBox()
        # y.installEventFilter(self)
        y.currentIndexChanged.connect(self.on_sth_changed)
        # y.setValidator(QIntValidator())
        x.setBuddy(y)
        y.addItems(Bands.bands.keys())
        pp.append((x, y, "&Band name", "UBVRI-x system", ""))
        ###
        x = self.label_x = QLabel()
        y = self.checkbox_force_parametric = QCheckBox()
        y.stateChanged.connect(self.on_sth_changed)
        x.setBuddy(y)
        pp.append((x, y, "&Force parametric?", "(even when tabular data is available)", ""))

        for i, (label, edit, name, short_descr, long_descr) in enumerate(pp):
            # label.setStyleSheet("QLabel {text-align: right}")
            assert isinstance(label, QLabel)
            label.setText(enc_name_descr(name, short_descr))
            label.setAlignment(Qt.AlignRight)
            lg.addWidget(label, i, 0)
            lg.addWidget(edit, i, 1)
            label.setToolTip(long_descr)
            edit.setToolTip(long_descr)

        lantanide.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))


        # #### Tab containing 3D plot representation
        w0 = keep_ref(QWidget())
        lantanide.addWidget(w0)
        self.figure0, self.canvas0, self.lfig0 = get_matplotlib_layout(w0, False)

        style_checkboxes(self)
        self.flag_process_changes = True

        self.__update()


    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Interface

    def band_name(self):
        return str(self.cb_band.currentText())

    def set_band_name(self, x):
        self.cb_band.setEditText(x)
        self.__update()

    def flag_force_parametric(self):
        return self.checkbox_force_parametric.isChecked()

    def set_flag_force_parametric(self, x):
        self.checkbox_force_parametric.setChecked(bool(x))


    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Slots

    def on_sth_changed(self):
        if self.flag_process_changes:
            self.__update()

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Internal gear

    def __update(self):
        self.flag_process_changes = False
        try:
            self.plot_band_curve()
        finally:
            self.flag_process_changes = True

    def plot_band_curve(self):
        try:
            # # Calculates stuff
            name = self.band_name()
            flag = self.flag_force_parametric()
            self._plot_scaling(name, flag)

        except Exception as E:
            self.parent_form.add_log_error(str(E))
            get_python_logger().exception("Could not plot band_curve")

