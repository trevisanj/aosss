"""Widget to edit a scaling factor for a Spectrum object."""

__all__ = ["WScaleSpectrum"]

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
# from filesky import *
# from fileccube import *
# from a_WChooseSpectrum import *
import os
import math
import numbers
import copy
import datetime
import traceback as tb
from pymos import *
from .a_WBand import *

class WScaleSpectrum(WBase):
    def __init__(self, parent):
        WBase.__init__(self, parent)

        def keep_ref(obj):
            self.__refs.append(obj)
            return obj

        self.__refs = []
        # Whether all the values in the fields are valid or not
        self.flag_valid = False
        # Internal flag to prevent taking action when some field is updated programatically
        self.flag_process_changes = False
        self.spectrum = None # Spectrum object


        # # Central layout
        lantanide = self.centralLayout = QVBoxLayout()
        lantanide.setMargin(0)
        self.setLayout(lantanide)


        # ## Horizontal splitter occupying main area: (options area) | (plot area)
        sp2 = self.splitter2 = QSplitter(Qt.Horizontal)
        lantanide.addWidget(sp2)

        ###
        wleft = keep_ref(QWidget())
        lwleft = QVBoxLayout(wleft)
        lwleft.setMargin(3)
        ###
        lwleft.addWidget(keep_ref(QLabel("<b>Reference band</b>")))
        ###
        y = self.chooseband = WBand(self.parent_form)
        lwleft.addWidget(y)
        y.edited.connect(self.on_scaling_edited)
        ###

        lgrid = keep_ref(QGridLayout())
        lwleft.addLayout(lgrid)
        lgrid.setMargin(0)
        lgrid.setVerticalSpacing(4)
        lgrid.setHorizontalSpacing(5)

        # field map: [(label widget, edit widget, field name, short description, long description), ...]
        pp = self._map0 = []
        ###
        x = self.label_x = QLabel()
        y = self.lineEdit_mag = QLineEdit()
        y.textEdited.connect(self.on_scaling_edited)
        x.setBuddy(y)
        pp.append((x, y, "Apparent &magnitude (?)", "", ""))
        ###


        for i, (label, edit, name, short_descr, long_descr) in enumerate(pp):
            # label.setStyleSheet("QLabel {text-align: right}")
            assert isinstance(label, QLabel)
            label.setText(enc_name_descr(name, short_descr))
            label.setAlignment(Qt.AlignRight)
            lgrid.addWidget(label, i, 0)
            lgrid.addWidget(edit, i, 1)
            label.setToolTip(long_descr)
            edit.setToolTip(long_descr)



        # #### Tab containing 3D plot representation
        wright = keep_ref(QWidget())
        self.figure0, self.canvas0, self.lfig0 = get_matplotlib_layout(wright)


        # ### Finally ...
        sp2.addWidget(wleft)
        sp2.addWidget(wright)


        self.setEnabled(False)  # disabled until load() is called
        style_checkboxes(self)
        self.flag_process_changes = True

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Interface


    def band_name(self):
        return str(self.cb_band.currentText())

    def flag_force_parametric(self):
        return self.checkbox_force_parametric.isChecked()

    def set_spectrum(self, x):
        assert isinstance(x, Spectrum)
        self.spectrum = x
        self.setEnabled(True)
        self.__update()

    def set_flag_force_parametric(self, x):
        self.checkbox_force_parametric.setChecked(bool(x))
        self.__update()

    def set_band_name(self, x):
        self.cb_band.setEditText(x)
        self.__update()

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
            fig = self.figure0
            fig.clear()
            name = self.band_name()
            flag = self.flag_force_parametric()
            _plot_scaling(fig, self.spectrum, self.band_name(), self.flag_force_parametric())
        except Exception as E:
            self.parent_form.add_log_error(str(E))
            get_python_logger().exception("Could not plot band_curve")
        finally:
            self.flag_process_changes = True


def _plot_scaling(self, fig, spectrum, band_name, flag_force_parametric):
    axarr = fig.subplots(3, 1, sharex=True, squeeze=False)

    MARGIN_H = .15  # extends horizontally beyond band range
    MARGIN_V = .02  # extends vertically beyond band range
    COLOR_OTHER_BANDS = (.4, .4, .4)
    COLOR_CURRENT_BAND = (.1, .1, .1)
    COLOOR_FILL_BAND = (.9, .8, .8)
    LINE_WIDTH = 3


    # calculations
    band_l0, band_lf = Bands.range(band_name, flag_force_parametric)  # band practical limits
    band_span_x = band_lf - band_l0
    plot_l0, plot_lf = band_l0-band_span_x*MARGIN_H, band_lf+band_span_x*MARGIN_H
    band_f = Bands.ufunc_band(band_name, flag_force_parametric)  # callable that returns the gain
    band_area = scipy.integrate.quad(band_f, band_l0, band_lf)[0]
    band_x = np.linspace(band_l0, band_lf, 200)
    band_y = band_f(band_x)
    band_max_y = max(band_y)



    # Second subplot
    ax = axarr[1, 0]

    # plt.xkcd()
    for band in Bands.bands.itervalues():
        l0, lf = band.range(flag_force_parametric)
        if lf >= plot_l0 and l0 <= plot_lf:
            x = np.linspace(l0, lf, 200)
            ax.plot(x, band.ufunc_band(flag_force_parametric)(x), c=COLOR_FILL_BAND, lw=LINE_WIDTH)
    ax.fill_between(band_x, band_y, color=COLOR_FILL_BAND)
    ax.set_xlim([band_l0 - band_span_x, band_lf + band_span_x])
    ax.set_ylim([0, band_max_y * (1 + MARGIN_H)])
    ax.set_xlabel("Wavelenght ($\AA$)")
    ax.set_ylabel("Gain")
    ax.annotate("Area=%g" % band_area, xy=((band_l0 + band_lf) / 2, band_max_y * .2), horizontalalignment="center")
    fig.tight_layout()
    self.canvas0.draw()

