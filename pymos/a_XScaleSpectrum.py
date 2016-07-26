"""Window to edit a scaling factor"""

__all__ = ["XScaleSpectrum"]

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import traceback as tb
import datetime
from pyfant import *
from pyfant.gui import *
from pymos import *
import os
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
#import scipy
#from scipy.interpolate import interp1d


class XScaleSpectrum(XLogDialog):
    """Application template with file operations in two tabs: (application area) and (log)"""

    def __init__(self, parent=None, file_main=None, file_abonds=None):
        XLogDialog.__init__(self, parent)

        def keep_ref(obj):
            self._refs.append(obj)
            return obj

        # Internal flag to prevent taking action when some field is updated programatically
        self.flag_process_changes = False
        self.spectrum = None  # Spectrum object
        self.cmag = None
        self.factor_ = None

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
        # lwleft.addWidget(keep_ref(QLabel("<b>Reference band</b>")))
        # ###

        lgrid = keep_ref(QGridLayout())
        lwleft.addLayout(lgrid)
        lgrid.setMargin(0)
        lgrid.setVerticalSpacing(4)
        lgrid.setHorizontalSpacing(5)

        # field map: [(label widget, edit widget, field name, short description, long description), ...]
        pp = self._map0 = []
        signals = []  # for the SignalProxy below
        ###
        x = keep_ref(QLabel())
        y = self.cb_band = QComboBox()
        signals.append(y.currentIndexChanged)
        x.setBuddy(y)
        y.addItems(Bands.bands.keys())
        pp.append((x, y, "&Band name", "UBVRI-x system", ""))
        ###
        x = self.label_x = QLabel()
        y = self.checkbox_force_parametric = QCheckBox()
        signals.append(y.stateChanged)
        x.setBuddy(y)
        pp.append((x, y, "&Force parametric?", "(even when tabular data is available)", ""))
        ###
        x = keep_ref(QLabel())
        y = self.edit_ref_jy = QLineEdit()
        y.setReadOnly(True)
        x.setBuddy(y)
        pp.append((x, y, "Ref Jy", "", ""))
        ###
        x = keep_ref(QLabel())
        y = self.edit_calc_jy = QLineEdit()
        y.setReadOnly(True)
        x.setBuddy(y)
        pp.append((x, y, "Calculated Jy", "", ""))
        ###
        x = keep_ref(QLabel())
        y = self.edit_calc_mag = QLineEdit()
        y.setReadOnly(True)
        x.setBuddy(y)
        pp.append((x, y, "Calculated apparent magnitude", "", ""))
        ###
        x = self.label_x = QLabel()
        y = self.spinBox_mag = QDoubleSpinBox()
        y.setSingleStep(.1)
        y.setDecimals(3)
        y.setMinimum(-100)
        y.setMaximum(100)
        signals.append(y.valueChanged)
        x.setBuddy(y)
        pp.append((x, y, "Desired apparent &magnitude", "", ""))
        ###
        x = keep_ref(QLabel())
        y = self.edit_calc_factor = QLineEdit()
        y.setReadOnly(True)
        x.setBuddy(y)
        pp.append((x, y, "Resulting Scaling factor", "", ""))
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

        lwleft.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))


        bb = keep_ref(QDialogButtonBox())
        bb.setOrientation(Qt.Horizontal)
        bb.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        lwleft.addWidget(bb)

        bb.rejected.connect(self.reject)
        bb.accepted.connect(self.accept)

        # #### Plot area
        wright = keep_ref(QWidget())
        self.figure0, self.canvas0, self.lfig0 = get_matplotlib_layout(wright)

        sp2.addWidget(wleft)
        sp2.addWidget(wright)

        # # Signal proxy
        # Limits the number of times that on_sth_changed() is called
        self.signal_proxy = SignalProxy(signals, delay=0.3, rateLimit=0, slot=self.on_sth_changed)

        self.setEnabled(False)  # disabled until load() is called
        style_checkboxes(self)
        self.flag_process_changes = True

        # self.__update()

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

    def desired_magnitude(self):
        return self.spinBox_mag.value()

    def calculated_magnitude(self):
        return self.cmag

    def factor(self):
        return self.factor_

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Qt override

    def accept(self):
        if self.factor_ is None or np.isinf(self.factor_):
            mag = QMessageBox.critical(None, "Cannot scale", "Scaling factor cannot be calculated")
            return False
        QDialog.accept(self)

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
            carea, cmag = _calculate_and_plot(fig, self.spectrum, self.band_name(), self.flag_force_parametric())
            self.canvas0.draw()

            # Updates calculated state
            self.cmag = cmag
            band = Bands.bands[name]
            self.edit_ref_jy.setText("%.2f" % band.ref_jy if band.ref_jy else "(not available)")
            self.edit_calc_jy.setText("%.2f" % carea)
            self.edit_calc_mag.setText(str(cmag) if cmag is not None else "(cannot calculate)")
            self.__update_factor()

        except Exception as E:
            self.add_log_error(str(E))
            get_python_logger().exception("Could not plot band_curve")
        finally:
            self.flag_process_changes = True

    def __update_factor(self):
        mag = self.desired_magnitude()
        cmag = self.calculated_magnitude()
        text = "(cannot calculate)"
        self.factor_ = None
        if cmag is not None:
            self.factor_ = k = MAGNITUDE_BASE ** (cmag - mag)
            text = str(k)
        self.edit_calc_factor.setText(text)

def _calculate_and_plot(fig, spectrum, band_name, flag_force_parametric):
    # axarr = fig.add_subplots(3, 1, sharex=True, squeeze=False)

    MARGIN_H = .15  # extends horizontally beyond band range
    MARGIN_V = .2  # extends vertically beyond band range
    COLOR_OTHER_BANDS = (.4, .4, .4)
    COLOR_CURRENT_BAND = (.1, .1, .1)
    COLOR_FILL_BAND = (.9, .8, .8)
    LINE_WIDTH = 2
    fmt_area = lambda x: "Area: %.1f" % x

    # # Calculations
    band = Bands.bands[band_name]
    band_l0, band_lf = band.range(flag_force_parametric)  # band practical limits
    band_span_x = band_lf - band_l0
    plot_l0, plot_lf = band_l0 - band_span_x * MARGIN_H, band_lf + band_span_x * MARGIN_H
    plot_h_middle = (plot_l0 + plot_lf) / 2
    band_f = band.ufunc_band(flag_force_parametric)  # callable that returns the gain
    # band_area = scipy.integrate.quad(band_f, band_l0, band_lf)[0]
    band_x = np.linspace(band_l0, band_lf, 200)
    band_y = band_f(band_x)
    band_area = np.trapz(band_y, band_x)
    band_max_y = max(band_y)
    spp = cut_spectrum(spectrum, plot_l0, plot_lf)  # spectrum for plotting
    spc = cut_spectrum(spectrum, band_l0, band_lf)  # spectrum for calculation
    out_y = spc.y * band_f(spc.x)
    flux_ylim = [0, np.max(spp.y) * (1 + MARGIN_V)] if len(spp) > 0 else [-.1, .1]

    # Calculates apparent magnitude and filtered flux area
    out_mag, out_area = None, 0
    if band.ref_jy:
        if len(spc) > 0:
            # out_f = interp1d(spc.x, out_y, bounds_error=False, fill_value=0)
            # out_area = scipy.integrate.quad(out_f, spc.x[0], spc.x[-1])[0]
            out_area = np.trapz(out_y, spc.x)
            out_mag = -2.5 * np.log10(out_area / band.ref_jy)
        else:
            out_mag = np.inf

    # # First subplot
    ax = fig.add_subplot(311)
    if len(spc) == 0:
        ax.plot([], [])
        ax.annotate("Band out of spectral range [%g, %g]" % (spectrum.x[0], spectrum.x[-1]), xy=(plot_h_middle, 0),
                    horizontalalignment="center", verticalalignment="center")
    else:
        ax.plot(spp.x, spp.y, c=COLOR_CURRENT_BAND, lw=LINE_WIDTH)
    # ax.plot(spc.x, spc.y, c=COLOR_CURRENT_BAND, lw=LINE_WIDTH, zorder=999)
    ax.set_xlim([plot_l0, plot_lf])
    ax.set_ylim(flux_ylim)
    ax.set_ylabel("Flux")

    # # Second subplot
    ax = fig.add_subplot(312)
    # other bands
    for band in Bands.bands.itervalues():
        l0, lf = band.range(flag_force_parametric)
        if lf >= plot_l0 and l0 <= plot_lf:
            x = np.linspace(l0, lf, 200)
            y = band.ufunc_band(flag_force_parametric)(x)
            ax.plot(x, y, c=COLOR_OTHER_BANDS, lw=LINE_WIDTH)
            idx_max = np.argmax(y)
            max_y = y[idx_max]
            overall_max_y = max(max_y, band_max_y)
            ax.annotate(band.name, xy=(x[idx_max], y[idx_max] + .1),
                        horizontalalignment="center", verticalalignment="center")
    # current band
    ax.plot(band_x, band_y, c=COLOR_CURRENT_BAND, lw=LINE_WIDTH)
    ax.fill_between(band_x, band_y, color=COLOR_FILL_BAND)
    ax.set_xlim([plot_l0, plot_lf])
    ax.set_ylim([0, overall_max_y * (1 + MARGIN_V)])
    ax.set_ylabel("Gain")
    idx_max = np.argmax(band_y)
    ax.annotate(fmt_area(band_area), xy=(band_x[idx_max], band_max_y * .45),
                horizontalalignment="center", verticalalignment="center")

    # Third subplot
    # # First subplot
    ax = fig.add_subplot(313)
    if len(spc) == 0:
        ax.plot([], [])
        ax.annotate("Band out of spectral range [%g, %g]" % (spectrum.x[0], spectrum.x[-1]), xy=(plot_h_middle, 0),
                    horizontalalignment="center", verticalalignment="center")
    else:
        ax.plot(spc.x, out_y, c=COLOR_CURRENT_BAND, lw=LINE_WIDTH)
        ax.fill_between(spc.x, out_y, color=COLOR_FILL_BAND)
        ax.annotate(fmt_area(out_area), xy=((spc.x[0] + spc.x[-1]) / 2, max(out_y) * .45),
                    horizontalalignment="center", verticalalignment="center")
    ax.set_xlim([plot_l0, plot_lf])
    ax.set_ylabel("Filtered flux")
    ax.set_ylim(flux_ylim)
    ax.set_xlabel("Wavelenght ($\AA$)")

    fig.tight_layout()

    return out_area, out_mag
