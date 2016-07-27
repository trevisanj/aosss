"""Widget to edit a FileSky object."""

__all__ = ["WFileSky"]

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
from .a_XScaleSpectrum import *
from .a_WSpectrumTable import *

_COLORS_SQ = [(.1, .6, .5), (.5, .1, .7)]
_ITER_COLORS_SQ = cycle(_COLORS_SQ)


class WFileSky(WBase):
    """
    FileSky editor widget.

    Arguments:
      parent=None
    """

    def __init__(self, parent):
        WBase.__init__(self, parent)

        def keep_ref(obj):
            self._refs.append(obj)
            return obj

        # Whether all the values in the fields are valid or not
        self.flag_valid = False
        # Internal flag to prevent taking action when some field is updated programatically
        self.flag_process_changes = False
        # GUI update needed but cannot be applied immediately, e.g. visible range being edited
        # each flag for one tab
        self.flag_update_pending = [False, False]
        # callables to update each visualization tab
        self.map_update_vis = [self.plot_spectra, self.plot_colors]
        # Whether there is sth in yellow background in the Headers tab
        self.flag_header_changed = False
        self.f = None # FileSky object
        self.obj_square = None


        # # Central layout
        lantanide = self.centralLayout = QVBoxLayout()
        lantanide.setMargin(0)
        self.setLayout(lantanide)


        # ## Horizontal splitter occupying main area: (options area) | (plot area)
        sp2 = self.splitter2 = QSplitter(Qt.Horizontal)
        lantanide.addWidget(sp2)

        # ## Widget left of horizontal splitter, containing (File Line) / (Options area)
        wfilett0 = keep_ref(QWidget())
        lwfilett0 = QVBoxLayout(wfilett0)
        lwfilett0.setMargin(0)

        # ### Line showing the File Name
        wfile = keep_ref(QWidget())
        lwfilett0.addWidget(wfile)
        l1 = keep_ref(QHBoxLayout(wfile))
        l1.setMargin(0)
        l1.addWidget(keep_ref(QLabel("<b>File:<b>")))
        w = self.label_fn_sky = QLabel()
        l1.addWidget(w)
        l1.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # ### Tabbed widget occupying left of horizontal splitter (OPTIONS TAB)
        tt0 = self.tabWidgetOptions = QTabWidget(self)
        lwfilett0.addWidget(tt0)
        tt0.setFont(MONO_FONT)
        tt0.currentChanged.connect(self.current_tab_changed_options)

        # #### Tab: Vertical Splitter between "Place Spectrum" and "Existing Spectra"
        spp = QSplitter(Qt.Vertical)
        tt0.addTab(spp, "&Spectra")

        # ##### Place Spectrum area
        # Widget that will be handled by the scrollable area
        sa0 = keep_ref(QScrollArea())
        sa0.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        sa0.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        wscrw = keep_ref(QWidget())
        sa0.setWidget(wscrw)
        sa0.setWidgetResizable(True)
        ###
        lscrw = QVBoxLayout(wscrw)
        lscrw.setMargin(3)
        ###
        alabel = keep_ref(QLabel("<b>Place spectrum</b>"))
        lscrw.addWidget(alabel)
        ###
        # Place Spectrum variables & button
        lg = keep_ref(QGridLayout())
        lscrw.addLayout(lg)
        lg.setMargin(0)
        lg.setVerticalSpacing(4)
        lg.setHorizontalSpacing(5)
        # lscrw.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # field map: [(label widget, edit widget, field name, short description, long description), ...]
        pp = self._map0 = []
        ###
        x = self.label_sp = QLabel()
        y = self.choosesp = WChooseSpectrum()
        y.installEventFilter(self)
        y.edited.connect(self.on_colors_setup_edited)
        # y.setValidator(QIntValidator())
        x.setBuddy(y)
        pp.append((x, y, "&spectrum", ".dat, .fits ...", ""))
        ###
        x = self.label_x = QLabel()
        y = self.spinbox_X = QSpinBox()
        y.valueChanged.connect(self.on_place_spectrum_edited)
        y.setMinimum(0)
        y.setMaximum(100)
        x.setBuddy(y)
        pp.append((x, y, "&x", "x-coordinate<br>(pixels; 0-based)", ""))
        ###
        x = self.label_y = QLabel()
        # TODO more elegant as spinboxes
        y = self.spinbox_Y = QSpinBox()
        y.valueChanged.connect(self.on_place_spectrum_edited)
        y.setMinimum(0)
        y.setMaximum(100)
        x.setBuddy(y)
        pp.append((x, y, "&y", "y-coordinate", ""))
        # ##### FWHM maybe later
        # x = self.label_fwhm = QLabel()
        # y = self.lineEdit_fwhm = QLineEdit()
        # y.installEventFilter(self)
        # y.textEdited.connect(self.on_place_spectrum_edited)
        # y.setValidator(QDoubleValidator(0, 10, 5))
        # x.setBuddy(y)
        # pp.append((x, y, "f&whm", "full width at<br>half-maximum (pixels)", ""))


        for i, (label, edit, name, short_descr, long_descr) in enumerate(pp):
            # label.setStyleSheet("QLabel {text-align: right}")
            assert isinstance(label, QLabel)
            label.setText(enc_name_descr(name, short_descr))
            label.setAlignment(Qt.AlignRight)
            lg.addWidget(label, i, 0)
            lg.addWidget(edit, i, 1)
            label.setToolTip(long_descr)
            edit.setToolTip(long_descr)

        # button
        l = QHBoxLayout()
        lscrw.addLayout(l)
        l.setMargin(0)
        l.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        b = QPushButton("&Place spectrum")
        l.addWidget(b)
        b.clicked.connect(self.go_clicked)

        # ##### Existing Spectra area
        wex = QWidget()
        lwex = QVBoxLayout(wex)
        lwex.setMargin(3)
        ###
        lwex.addWidget(keep_ref(QLabel("<b>Existing spectra</b>")))
        ###
        w = self.wsptable = WSpectrumTable(self.parent_form)
        w.edited.connect(self.on_spectra_edited)
        lwex.addWidget(w)

        # ##### Finally...
        spp.addWidget(sa0)
        spp.addWidget(wex)


        # #### Second tab (NEW FileSky)
        sa1 = keep_ref(QScrollArea())
        tt0.addTab(sa1, "&Header")
        sa1.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        sa1.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Widget that will be handled by the scrollable area
        w = keep_ref(QWidget())
        sa1.setWidget(w)
        sa1.setWidgetResizable(True)
        lscrw = QVBoxLayout(w)
        lscrw.setMargin(3)
        ###
        lscrw.addWidget(keep_ref(QLabel("<b>Header properties</b>")))

        # Form layout
        lg = keep_ref(QGridLayout())
        lg.setMargin(0)
        lg.setVerticalSpacing(4)
        lg.setHorizontalSpacing(5)
        lscrw.addLayout(lg)
        ###
        lscrw.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # field map: [(label widget, edit widget, field name, short description, long description), ...]
        pp = self._map1 = []
        ###
        x = self.label_width = QLabel()
        y = self.spinbox_width = QSpinBox()
        y.valueChanged.connect(self.on_header_edited)
        y.setMinimum(1)
        y.setMaximum(100)
        x.setBuddy(y)
        pp.append((x, y, "&width", "hi-resolution (HR) width (pixels)", "", lambda: self.f.sky.width, lambda: self.spinbox_width.value()))
        ###
        x = self.label_height = QLabel()
        y = self.spinbox_height = QSpinBox()
        y.valueChanged.connect(self.on_header_edited)
        y.setMinimum(0)
        y.setMaximum(100)
        x.setBuddy(y)
        pp.append((x, y, "&height", "HR height (pixels)", "", lambda: self.f.sky.height, lambda: self.spinbox_height.value()))
        ###
        x = self.label_hrfactor = QLabel()
        y = self.spinbox_hrfactor = QSpinBox()
        y.valueChanged.connect(self.on_header_edited)
        y.setMinimum(1)
        y.setMaximum(100)
        x.setBuddy(y)
        pp.append((x, y, "&hrfactor", "(HR width)/(ifu width)", "", lambda: self.f.sky.hrfactor, lambda: self.spinbox_hrfactor.value()))
        ###
        x = self.label_hr_pix_size = QLabel()
        y = self.lineEdit_hr_pix_size = QLineEdit()
        y.installEventFilter(self)
        y.textEdited.connect(self.on_header_edited)
        y.setValidator(QDoubleValidator(0, 1, 7))
        x.setBuddy(y)
        pp.append((x, y, "&hr_pix_size", "HR pixel width/height (arcsec)", "", lambda: self.f.sky.hr_pix_size,
                   lambda: float(self.lineEdit_hr_pix_size.text())))
        ###
        x = self.label_hrfactor = QLabel()
        y = self.spinbox_R = QSpinBox()
        y.valueChanged.connect(self.on_header_edited)
        y.setMinimum(100)
        y.setMaximum(100000)
        y.setSingleStep(100)
        x.setBuddy(y)
        pp.append((x, y, "&R", "resolution (delta lambda)/lambda", "", lambda: self.f.sky.R, lambda: self.spinbox_R.value()))

        for i, (label, edit, name, short_descr, long_descr, f_from_f, f_from_edit) in enumerate(pp):
            # label.setStyleSheet("QLabel {text-align: right}")
            assert isinstance(label, QLabel)
            label.setText(enc_name_descr(name, short_descr))
            label.setAlignment(Qt.AlignRight)
            lg.addWidget(label, i, 0)
            lg.addWidget(edit, i, 1)
            label.setToolTip(long_descr)
            edit.setToolTip(long_descr)

        lgo = QHBoxLayout()
        lgo.setMargin(0)
        lscrw.addLayout(lgo)
        ###
        bgo = self.button_revert = QPushButton("Revert")
        lgo.addWidget(bgo)
        bgo.clicked.connect(self.header_revert)
        ###
        bgo = self.button_apply = QPushButton("Apply")
        lgo.addWidget(bgo)
        bgo.clicked.connect(self.header_apply)
        ###
        lgo.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # #### More Tools tab
        wset = keep_ref(QWidget())
        tt0.addTab(wset, "&More")
        lwset = keep_ref(QVBoxLayout(wset))
        ###
        b = keep_ref(QPushButton("&Crop in new window..."))
        lwset.addWidget(b)
        b.clicked.connect(self.crop_clicked)
        ###
        b = keep_ref(QPushButton("E&xport ... %s" % FileCCube.description))
        lwset.addWidget(b)
        b.clicked.connect(self.export_ccube_clicked)
        ###
        lwset.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding    ))


        # ### Tabbed widget occupying right of horizontal splitter
        tt1 = self.tabWidgetVis = QTabWidget(self)
        tt1.setFont(MONO_FONT)
        tt1.currentChanged.connect(self.current_tab_changed_vis)

        # #### Tab containing 3D plot representation
        w0 = keep_ref(QWidget())
        tt1.addTab(w0, "&Plot 3D")
        # http://stackoverflow.com/questions/12459811
        self.figure0, self.canvas0, self.lfig0 = get_matplotlib_layout(w0)

        # lscrw.addLayout(lfig)

        # #### Colors tab
        w1 = keep_ref(QWidget())
        tt1.addTab(w1, "&Colors")
        ###
        lw1 = QVBoxLayout(w1)
        lwset = keep_ref(QHBoxLayout())
        lw1.addLayout(lwset)
        ###
        la = keep_ref(QLabel("&Visible range"))
        lwset.addWidget(la)
        ###
        ed = self.lineEdit_visibleRange = QLineEdit("[3800., 7500.]")
        lwset.addWidget(ed)
        la.setBuddy(ed)
        ed.textEdited.connect(self.on_colors_setup_edited)
        ###
        la = keep_ref(QLabel("Color map"))
        lwset.addWidget(la)
        ###
        ed = self.comboBox_cmap = QComboBox()
        ed.addItem("0-Rainbow")
        ed.addItem("1-RGB")
        ed.setCurrentIndex(0)
        lwset.addWidget(ed)
        la.setBuddy(ed)
        ed.currentIndexChanged.connect(self.on_colors_setup_edited)
        ###
        cb = self.checkBox_scale = QCheckBox("Scale colors")
        lwset.addWidget(cb)
        # cb.setTooltip("If checked, will make color luminosity proportional to flux area under the visible range")
        cb.stateChanged.connect(self.on_colors_setup_edited)
        ###
        b = keep_ref(QPushButton("Redra&w"))
        lwset.addWidget(b)
        b.clicked.connect(self.replot_colors)
        ###
        lwset.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        ###
        wm = keep_ref(QWidget())
        # wm.setMargin(0)
        lw1.addWidget(wm)
        self.figure1, self.canvas1, self.lfig1 = get_matplotlib_layout(wm)
        self.canvas1.mpl_connect('button_press_event', self.on_colors_click)

        # ### Finally ...
        sp2.addWidget(wfilett0)
        sp2.addWidget(tt1)


        # # Timers
        ##########
        t = self.timer_place = QTimer(self)
        t.timeout.connect(self.timeout_place)
        t.setInterval(500)
        t.start()

        self.setEnabled(False)  # disabled until load() is called
        style_checkboxes(self)
        self.flag_process_changes = True
        self.add_log("Welcome from %s.__init__()" % (self.__class__.__name__))


    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Interface

    def load(self, x):
        assert isinstance(x, FileSky)
        self.f = x
        self.wsptable.set_collection(x.sky)
        self.__update_from_f(True)
        # this is called to perform file validation upon loading
        # TODO probably not like this
        self.__update_f()
        self.setEnabled(True)

    def get_selected_row_indexes(self):
        ii = list(set([index.row() for index in self.twSpectra.selectedIndexes()]))
        return ii

    def update_sky_headers(self, sky):
        """Updates heeaders of a Sky objects using contents of the Headers tab"""
        emsg, flag_error = "", False
        ss = ""
        try:
            ss = "width"
            sky.width = int(self.spinbox_width.value())
            ss = "height"
            sky.height = int(self.spinbox_height.value())
            ss = "hrfactor"
            sky.hrfactor = int(self.spinbox_hrfactor.value())
            ss = "hr_pix_size"
            sky.hr_pix_size = float(self.lineEdit_hr_pix_size.text())
            ss = "R"
            sky.R = float(self.spinbox_R.value())
            self.__update_from_f(True)
        except Exception as E:
            flag_error = True
            if ss:
                emsg = "Field '%s': %s" % (ss, str(E))
            else:
                emsg = str(E)
            self.add_log_error(emsg)
        return not flag_error

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Qt override

    def setFocus(self, reason=None):
        """Sets focus to first field. Note: reason is ignored."""
        # TODO self.lineEdit_titrav.setFocus()

    def eventFilter(self, source, event):
        if event.type() == QEvent.FocusIn:
            # text = random_name()
            # self.__add_log(text)
            pass

        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Delete:
                print "TUQUEJMI TUQUEJMI"
                if source == self.twSpectra:
                    print "ABOUT TO DELETE SPECTRA"
                    n_deleted = self.__delete_spectra()
                    if n_deleted > 0:
                        self.edited.emit()
        return False

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Slots

    def on_colors_setup_edited(self):
        if self.flag_process_changes:
            self.flag_update_pending[1] = True

    def on_header_edited(self):
        if self.flag_process_changes:
            sth = False
            sndr = self.sender()
            for _, edit, _, _, _, f_from_f, f_from_edit in self._map1:
                changed = f_from_f() != f_from_edit()
                sth = sth or changed
                if edit == sndr:
                    style_widget(self.sender(), changed)
            self.set_flag_header_changed(sth)

    def on_spectra_edited(self):
        self.__update_from_f()
        self.edited.emit()

    def on_place_spectrum_edited(self):
        # could only update the obj_square but this is easier
        self.plot_colors()

    def go_clicked(self):
        print "GO CLICKED\n"*10
        flag_emit = False
        try:
            x, y = self.get_place_spectrum_xy()
            sp = self.choosesp.sp
            if not sp:
                raise RuntimeError("Spectrum not loaded")
            sp.pixel_x, sp.pixel_y = x, y
            self.f.sky.add_spectrum(sp)
            self.__update_from_f()
            flag_emit = True
        except Exception as E:
            self.add_log_error(str(E), True)
            raise
        if flag_emit:
            self.edited.emit()

    def header_revert(self):
        self.__update_from_f_headers()

    def header_apply(self):
        if self.update_sky_headers(self.f.sky):
            self.__update_from_f(True)

    def current_tab_changed_vis(self):
        self.__update_vis_if_pending()

    def current_tab_changed_options(self):
        pass

    def timeout_place(self):
        if self.obj_square:
            next_color = _ITER_COLORS_SQ.next()
            for obj in self.obj_square:
                obj.set_color(next_color)
                self.canvas1.draw()

    def crop_clicked(self):
        try:
            sky = self.f.sky

            specs = (("x_range", {"value": "[%d, %d]" % (0, sky.width - 1)}),
                     ("y_range", {"value": "[%d, %d]" % (0, sky.height - 1)}),
                     ("wavelength_range", {"value": "[%g, %g]" % (sky.wavelength[0], sky.wavelength[-1])})
                     )
            # fields = ["x_range", "y_range", "wavelength_range"]
            form = XParametersEditor(specs=specs, title="Select sub-cube")
            while True:
                r = form.exec_()
                if not r:
                    break
                kk = form.GetKwargs()
                s = ""
                try:
                    s = "x_range"
                    x0, x1 = eval(kk["x_range"])
                    s = "y_range"
                    y0, y1 = eval(kk["y_range"])
                    s = "wavelength_range"
                    lambda0, lambda1 = eval(kk["wavelength_range"])
                except Exception as E:
                    self.add_log_error("Failed evaluating %s: %s: %s" % (s, E.__class__.__name__, str(E)), True)
                    continue

                # Works with clone, then replaces original, to ensure atomic operation
                clone = copy.deepcopy(self.f)
                clone.filename = None
                try:
                    clone.sky.crop(x0, x1, y0, y1, lambda0, lambda1)
                except Exception as E:
                    self.add_log_error("Crop operation failed: %s: %s" % (E.__class__.__name__, str(E)), True)
                    continue

                form1 = self.keep_ref(self.parent_form.__class__())
                form1.load(clone)
                form1.show()

                # # Replaces original
                # self.f = clone
                # self.__update_from_f(True)
                break

        except Exception as E:
            self.add_log_error("Crop failed: %s" % str(E), True)
            raise

    def export_ccube_clicked(self):
        fn = QFileDialog.getSaveFileName(self, "Save file in %s format" % FileCCube.description,
                                         FileCCube.default_filename, "*.fits")
        if fn:
            try:
                fn = str(fn)
                ccube = self.f.sky.to_compass_cube()
                fccube = FileCCube()
                fccube.ccube = ccube
                fccube.save_as(fn)
            except Exception as E:
                self.add_log_error("Failed export: %s: %s" % (E.__class__.__name__, str(E)), True)
                raise

    def replot_colors(self):
        self.plot_colors()

    def on_colors_click(self, event):
        x, y = int(event.xdata+.5), int(event.ydata+.5)
        if 0 <= x < self.f.sky.width and 0 <= y < self.f.sky.height:
            self.spinbox_X.setValue(x)
            self.spinbox_Y.setValue(y)
            self.plot_colors()

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Internal gear

    def get_place_spectrum_xy(self):
        x = int(self.spinbox_X.value())
        if not (0 <= x < self.f.sky.width):
            raise RuntimeError("x must be in [0, %s)" % self.f.sky.width)
        y = int(self.spinbox_Y.value())
        if not (0 <= y < self.f.sky.height):
            raise RuntimeError("y must be in [0, %s)" % self.f.sky.height)
        return x, y

    def __update_from_f(self, flag_headers=False):
        """
          flag_headers -- resets header widgets as well
        """
        self.flag_process_changes = False
        try:
            self.update_label_fn()
            self.wsptable.update()

            idx = self.tabWidgetVis.currentIndex()
            for i, callable_ in enumerate(self.map_update_vis):
                # Updates current visualization tab and flags update pending for other tabs
                if i == idx:
                    callable_()
                    self.flag_update_pending[i] = False
                else:
                    self.flag_update_pending[i] = True

            if flag_headers:
                self.__update_from_f_headers()

        finally:
            self.flag_process_changes = True

    def update_label_fn(self):
        if not self.f:
            text = "(not loaded)"
        elif self.f.filename:
            text = os.path.relpath(self.f.filename, ".")
        else:
            text = "(filename not set)"
        self.label_fn_sky.setText(text)

    def __update_from_f_headers(self):
        """Updates header controls only"""
        sky = self.f.sky
        self.spinbox_width.setValue(sky.width)
        self.spinbox_height.setValue(sky.height)
        self.spinbox_hrfactor.setValue(sky.hrfactor)
        self.lineEdit_hr_pix_size.setText(str(sky.hr_pix_size))
        self.spinbox_R.setValue(sky.R)
        self.set_flag_header_changed(False)

    def _update_labels_fn(self):
        cwd = os.getcwd()
        for editor, label in zip(self.editors, self.labels_fn):
            if not label:
                continue
            if not editor.f:
                text = "(not loaded)"
            elif editor.f.filename:
                text = os.path.relpath(editor.f.filename, ".")
            else:
                text = "(filename not set)"
            label.setText(text)

    def set_flag_header_changed(self, flag):
        self.button_apply.setEnabled(flag)
        self.button_revert.setEnabled(flag)
        self.flag_header_changed = flag
        if not flag:
            # If not changed, removes all eventual yellows
            for _, edit, _, _, _, _, _ in self._map1:
                style_widget(edit, False)

    def __update_f(self):
        o = self.f
        sky = self.f.sky
        self.flag_valid = self.update_sky_headers(sky)

    def __delete_spectra(self):
        ii = self.get_selected_row_indexes()
        if len(ii) > 0:
            self.f.sky.delete_spectra(ii)
            self.__update_from_f()
        return len(ii)

    def __update_vis_if_pending(self):
        idx = self.tabWidgetVis.currentIndex()
        if self.flag_update_pending[idx]:
            self.map_update_vis[idx]()
            self.flag_update_pending[idx] = False

    def plot_spectra(self):
        # self.clear_markers()
        if self.f is None:
            return

        try:
            fig = self.figure0
            fig.clear()
            ax = fig.gca(projection='3d')
            _plot_spectra(ax, self.f.sky)
            fig.tight_layout()
            self.canvas0.draw()

        except Exception as E:
            self.add_log_error(str(E))
            get_python_logger().exception("Could not plot spectra")

    def plot_colors(self):
        # self.clear_markers()
        if self.f is None:
            return

        try:
            vrange = eval(str(self.lineEdit_visibleRange.text()))
            if len(vrange) != 2 or not all([isinstance(x, numbers.Number) for x in vrange]):
                raise RuntimeError('Visible range must be a sequence with two numbers')

            fig = self.figure1
            fig.clear()
            ax = fig.gca()
            sqx, sqy = None, None
            flag_scale = self.checkBox_scale.isChecked()
            method = self.comboBox_cmap.currentIndex()
            try:
                sqx, sqy = self.get_place_spectrum_xy()
            except:
                pass  # Nevermind (does not draw square)
            self.obj_square = _plot_colors(ax, self.f.sky, vrange, sqx, sqy, flag_scale, method)

            fig.tight_layout()
            self.canvas1.draw()

            self.flag_plot_colors_pending = False
        except Exception as E:
            self.add_log_error(str(E))
            get_python_logger().exception("Could not plot colors")


def _plot_spectra(ax, sky):
    """
    Plots front and back grid, scaled fluxes

    data cube            mapped to 3D axis
    ------------------   -----------------
    X pixel coordinate   x
    Y pixel coordinate   z
    Z wavelength         y
    """
    assert isinstance(sky, Sky)

    flag_empty = len(sky.spectra) == 0
    r0 = [-.5, sky.width + .5]
    r2 = [-.5, sky.height + .5]
    if flag_empty:
        r1 = [-.5, .5]
    else:
        max_flux = max([max(sp.flux) for sp in sky.spectra])
        _y = sky.wavelength
        dlambda = _y[1]-_y[0]
        r1 = [_y[0] - dlambda / 2, _y[-1] + dlambda / 2]
        scale = 1./max_flux

    PAR = {"color": "y", "alpha": 0.3}
    def draw_line(*args):
        ax.plot3D(*args, **PAR)


    # draws cube
    if not flag_empty:
        for s, e in combinations(np.array(list(product(r0, r1, r2))), 2):
            if np.sum(s == e) == 2:
            # if np.sum(np.abs(s - e)) == r[1] - r[0]:
                draw_line(*zip(s, e))


    # draws grids
    for i in range(sky.width+1):
        draw_line([i-.5]*2, [r1[0]]*2, r2)
        draw_line([i-.5]*2, [r1[1]]*2, r2)
    for i in range(sky.height + 1):
        draw_line(r0, [r1[0]]*2, [i-.5]* 2)
        draw_line(r0, [r1[1]]*2, [i-.5]* 2)


    for sp in sky.spectra:
        n = len(sp)
        flux1 = sp.flux * scale + sp.pixel_y - .5
        ax.plot(np.ones(n) * sp.pixel_x,
                sp.wavelength,
                flux1, color='k')

    # ax.set_aspect("equal")
    ax.set_xlabel("x (pixel)")
    ax.set_ylabel('wavelength ($\AA$)')  # ax.set_ylabel('wavelength ($\AA$)')
    ax.set_zlabel('y (pixel)')
    # ax.set_zlabel('?')
    # plt.show()


def _plot_colors(ax, sky, vrange, sqx=None, sqy=None, flag_scale=False, method=0):
    """
    Plots image on axis

    Arguments
      ax -- matplotlib axis
      sky -- Sky instance
      vrange -- visible range
      sqx -- "place spectrum" x
      sqy -- "place spectrum" y

    Returns: matplotlib plot object representing square, or None
    """
    assert isinstance(sky, Sky)
    im = sky.to_colors(vrange, flag_scale, method)
    ax.imshow(im, interpolation="nearest")
    ax.invert_yaxis()
    obj_square = None
    K = .5
    if sqx is not None:
        x0, x1, y0, y1 = sqx-K, sqx+K, sqy-K, sqy+K
        obj_square = ax.plot([x0, x1, x1, x0, x0], [y0, y0, y1, y1, y0],
                             c=_COLORS_SQ[0], ls='solid', lw=3, alpha=0.5, zorder=99999)
    ax.set_xlim([-K, sky.width-.5])
    ax.set_ylim([-K, sky.height-.5])
    return obj_square

