__all__ = ["WFileSparseCube"]

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
from .a_WSpectrumCollection import *

_COLORS_SQ = [(.1, .6, .5), (.5, .1, .7)]
_ITER_COLORS_SQ = cycle(_COLORS_SQ)


class WFileSparseCube(WBase):
    """
    FileSparseCube editor widget.

    Arguments:
      parent=None
    """

    def __init__(self, parent):
        WBase.__init__(self, parent)

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
        self.f = None  # FileSparseCube object
        self.obj_square = None

        # # Central layout
        lantanide = self.centralLayout = QVBoxLayout()
        lantanide.setMargin(0)
        self.setLayout(lantanide)

        # ## Horizontal splitter occupying main area: (options area) | (plot area)
        sp2 = self.splitter2 = QSplitter(Qt.Horizontal)
        lantanide.addWidget(sp2)

        # ## Widget left of horizontal splitter, containing (File Line) / (Options area)
        wfilett0 = self.keep_ref(QWidget())
        lwfilett0 = QVBoxLayout(wfilett0)
        lwfilett0.setMargin(0)

        # ### Line showing the File Name
        wfile = self.keep_ref(QWidget())
        lwfilett0.addWidget(wfile)
        l1 = self.keep_ref(QHBoxLayout(wfile))
        l1.setMargin(0)
        l1.addWidget(self.keep_ref(QLabel("<b>File:<b>")))
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
        sa0 = self.keep_ref(QScrollArea())
        sa0.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        sa0.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        wscrw = self.keep_ref(QWidget())
        sa0.setWidget(wscrw)
        sa0.setWidgetResizable(True)
        ###
        lscrw = QVBoxLayout(wscrw)
        lscrw.setMargin(3)
        ###
        alabel = self.keep_ref(QLabel("<b>Place spectrum</b>"))
        lscrw.addWidget(alabel)
        ###
        # Place Spectrum variables & button
        lg = self.keep_ref(QGridLayout())
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
        y.setMaximum(1000)
        x.setBuddy(y)
        pp.append((x, y, "&x", "x-coordinate<br>(pixels; 0-based)", ""))
        ###
        x = self.label_y = QLabel()
        # TODO more elegant as spinboxes
        y = self.spinbox_Y = QSpinBox()
        y.valueChanged.connect(self.on_place_spectrum_edited)
        y.setMinimum(0)
        y.setMaximum(1000)
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
        lwex.addWidget(self.keep_ref(QLabel("<b>Existing spectra</b>")))
        ###
        w = self.wsptable = WSpectrumCollection(self.parent_form)
        w.edited.connect(self.on_spectra_edited)
        lwex.addWidget(w)

        # ##### Finally...
        spp.addWidget(sa0)
        spp.addWidget(wex)

        # #### Second tab (NEW FileSparseCube)
        sa1 = self.keep_ref(QScrollArea())
        tt0.addTab(sa1, "&Header")
        sa1.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        sa1.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Widget that will be handled by the scrollable area
        w = self.keep_ref(QWidget())
        sa1.setWidget(w)
        sa1.setWidgetResizable(True)
        lscrw = QVBoxLayout(w)
        lscrw.setMargin(3)
        ###
        lscrw.addWidget(self.keep_ref(QLabel("<b>Header properties</b>")))
        ###
        b = self.keep_ref(QPushButton("Collect field names"))
        b.clicked.connect(self.on_collect_fieldnames)
        lscrw.addWidget(b)

        # Form layout
        lg = self.keep_ref(QGridLayout())
        lg.setMargin(0)
        lg.setVerticalSpacing(4)
        lg.setHorizontalSpacing(5)
        lscrw.addLayout(lg)
        ###
        lscrw.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # field map: [(label widget, edit widget, field name, short description, long description), ...]
        pp = self._map1 = []

        ###
        x = self.keep_ref(QLabel())
        y = self.edit_fieldnames = QPlainTextEdit()
        y.textChanged.connect(self.on_header_edited)
        x.setBuddy(y)
        pp.append((x, y, "&Field names", "'header' information for each spectrum", "", lambda: self.f.sparsecube.fieldnames,
                   lambda: self.edit_fieldnames.toPlainText()))
        ###
        x = self.label_width = QLabel()
        y = self.spinbox_width = QSpinBox()
        y.valueChanged.connect(self.on_header_edited)
        y.setMinimum(1)
        y.setMaximum(1000)
        x.setBuddy(y)
        pp.append((x, y, "&width", "hi-resolution (HR) width (pixels)", "", lambda: self.f.sparsecube.width,
                   lambda: self.spinbox_width.value()))
        ###
        x = self.label_height = QLabel()
        y = self.spinbox_height = QSpinBox()
        y.valueChanged.connect(self.on_header_edited)
        y.setMinimum(0)
        y.setMaximum(1000)
        x.setBuddy(y)
        pp.append(
            (x, y, "&height", "HR height (pixels)", "", lambda: self.f.sparsecube.height, lambda: self.spinbox_height.value()))
        ###
        x = self.label_hrfactor = QLabel()
        y = self.spinbox_hrfactor = QSpinBox()
        y.valueChanged.connect(self.on_header_edited)
        y.setMinimum(1)
        y.setMaximum(100)
        x.setBuddy(y)
        pp.append((x, y, "&hrfactor", "(HR width)/(ifu width)", "", lambda: self.f.sparsecube.hrfactor,
                   lambda: self.spinbox_hrfactor.value()))
        ###
        x = self.label_hr_pix_size = QLabel()
        y = self.lineEdit_hr_pix_size = QLineEdit()
        y.installEventFilter(self)
        y.textEdited.connect(self.on_header_edited)
        y.setValidator(QDoubleValidator(0, 1, 7))
        x.setBuddy(y)
        pp.append((x, y, "&hr_pix_size", "HR pixel width/height (arcsec)", "", lambda: self.f.sparsecube.hr_pix_size,
                   lambda: float(self.lineEdit_hr_pix_size.text())))
        ###
        x = self.label_hrfactor = QLabel()
        y = self.spinbox_R = QSpinBox()
        y.valueChanged.connect(self.on_header_edited)
        y.setMinimum(100)
        y.setMaximum(100000)
        y.setSingleStep(100)
        x.setBuddy(y)
        pp.append(
            (x, y, "&R", "resolution (delta lambda)/lambda", "", lambda: self.f.sparsecube.R, lambda: self.spinbox_R.value()))

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
        wset = self.keep_ref(QWidget())
        tt0.addTab(wset, "&More")
        lwset = self.keep_ref(QVBoxLayout(wset))
        ###
        b = self.keep_ref(QPushButton("&Crop in new window..."))
        lwset.addWidget(b)
        b.clicked.connect(self.crop_clicked)
        ###
        b = self.keep_ref(QPushButton("E&xport %s ..." % FileFullCube.description))
        lwset.addWidget(b)
        b.clicked.connect(self.export_ccube_clicked)
        ###
        lwset.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # ### Tabbed widget occupying right of horizontal splitter
        tt1 = self.tabWidgetVis = QTabWidget(self)
        tt1.setFont(MONO_FONT)
        tt1.currentChanged.connect(self.current_tab_changed_vis)

        # #### Tab containing 3D plot representation
        w0 = self.keep_ref(QWidget())
        tt1.addTab(w0, "&Plot 3D")
        # http://stackoverflow.com/questions/12459811
        self.figure0, self.canvas0, self.lfig0 = get_matplotlib_layout(w0)

        # lscrw.addLayout(lfig)

        # #### Colors tab
        w1 = self.keep_ref(QWidget())
        tt1.addTab(w1, "&Colors")
        ###
        lw1 = QVBoxLayout(w1)
        lwset = self.keep_ref(QHBoxLayout())
        lw1.addLayout(lwset)
        ###
        la = self.keep_ref(QLabel("&Visible range"))
        lwset.addWidget(la)
        ###
        ed = self.lineEdit_visibleRange = QLineEdit("[3800., 7500.]")
        lwset.addWidget(ed)
        la.setBuddy(ed)
        ed.textEdited.connect(self.on_colors_setup_edited)
        ###
        la = self.keep_ref(QLabel("Color map"))
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
        b = self.keep_ref(QPushButton("Redra&w"))
        lwset.addWidget(b)
        b.clicked.connect(self.replot_colors)
        ###
        lwset.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        ###
        wm = self.keep_ref(QWidget())
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
        assert isinstance(x, FileSparseCube)
        self.f = x
        self.wsptable.set_collection(x.sparsecube)
        self.__update_gui(True)
        self.flag_valid = True  # assuming that file does not come with errors
        self.setEnabled(True)

    def update_gui_label_fn(self):
        self.__update_gui_label_fn()

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Qt override

    def setFocus(self, reason=None):
        """Sets focus to first field. Note: reason is ignored."""
        # TODO self.lineEdit_titrav.setFocus()

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
        self.__update_gui_vis()
        self.edited.emit()

    def on_place_spectrum_edited(self):
        # could only update the obj_square but this is easier
        self.plot_colors()

    def go_clicked(self):
        print("GO CLICKED\n" * 10)
        flag_emit = False
        try:
            x, y = self.get_place_spectrum_xy()
            sp = self.choosesp.sp
            if not sp:
                raise RuntimeError("Spectrum not loaded")
            sp.pixel_x, sp.pixel_y = x, y
            self.f.sparsecube.add_spectrum(sp)
            self.__update_gui()
            flag_emit = True
        except Exception as E:
            self.add_log_error(str_exc(E), True)
            raise
        if flag_emit:
            self.edited.emit()

    def header_revert(self):
        self.__update_gui_header()

    def header_apply(self):
        if self.__update_f_header(self.f.sparsecube):
            self.__update_gui(True)

    def current_tab_changed_vis(self):
        self.__update_gui_vis_if_pending()

    def current_tab_changed_options(self):
        pass

    def timeout_place(self):
        if self.obj_square:
            next_color = next(_ITER_COLORS_SQ)
            for obj in self.obj_square:
                obj.set_color(next_color)
                self.canvas1.draw()

    def crop_clicked(self):
        try:
            sky = self.f.sparsecube

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
                kk = form.get_kwargs()
                s = ""
                try:
                    s = "x_range"
                    x0, x1 = eval(kk["x_range"])
                    s = "y_range"
                    y0, y1 = eval(kk["y_range"])
                    s = "wavelength_range"
                    lambda0, lambda1 = eval(kk["wavelength_range"])
                except Exception as E:
                    self.add_log_error("Failed evaluating %s: %s" % (s, str_exc(E)), True)
                    continue

                # Works with clone, then replaces original, to ensure atomic operation
                clone = copy.deepcopy(self.f)
                clone.filename = None
                try:
                    clone.sparsecube.crop(x0, x1, y0, y1, lambda0, lambda1)
                except Exception as E:
                    self.add_log_error("Crop operation failed: %s" % str_exc(E), True)
                    continue

                form1 = self.keep_ref(self.parent_form.__class__())
                form1.load(clone)
                form1.show()

                # # Replaces original
                # self.f = clone
                # self.__update_gui(True)
                break

        except Exception as E:
            self.add_log_error("Crop failed: %s" % str_exc(E), True)
            raise

    def export_ccube_clicked(self):
        fn = QFileDialog.getSaveFileName(self, "Save file in %s format" % FileFullCube.description,
                                         FileFullCube.default_filename, "*.fits")
        if fn:
            try:
                fn = str(fn)
                wcube = self.f.sparsecube.to_full_cube()
                fccube = FileFullCube()
                fccube.wcube = wcube
                fccube.save_as(fn)
            except Exception as E:
                self.add_log_error("Failed export: %s" % str_exc(E), True)
                raise

    def replot_colors(self):
        self.plot_colors()

    def on_colors_click(self, event):
        x, y = int(event.xdata + .5), int(event.ydata + .5)
        if 0 <= x < self.f.sparsecube.width and 0 <= y < self.f.sparsecube.height:
            self.spinbox_X.setValue(x)
            self.spinbox_Y.setValue(y)
            self.plot_colors()

    def on_collect_fieldnames(self):
        # TODO confirmation
        self.edit_fieldnames.setPlainText(str(self.f.sparsecube.collect_fieldnames()))

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Internal gear

    def __emit_if(self):
        if self.flag_process_changes:
            self.edited.emit()

    def get_place_spectrum_xy(self):
        x = int(self.spinbox_X.value())
        if not (0 <= x < self.f.sparsecube.width):
            raise RuntimeError("x must be in [0, %s)" % self.f.sparsecube.width)
        y = int(self.spinbox_Y.value())
        if not (0 <= y < self.f.sparsecube.height):
            raise RuntimeError("y must be in [0, %s)" % self.f.sparsecube.height)
        return x, y

    def __update_gui(self, flag_header=False):
        """Updates GUI to reflect what is in self.f"""
        self.flag_process_changes = False
        try:
            self.__update_gui_label_fn()
            self.wsptable.update()
            self.__update_gui_vis()
            if flag_header:
                self.__update_gui_header()
        finally:
            self.flag_process_changes = True

    def __update_gui_vis(self):
        idx = self.tabWidgetVis.currentIndex()
        for i, callable_ in enumerate(self.map_update_vis):
            # Updates current visualization tab and flags update pending for other tabs
            if i == idx:
                callable_()
                self.flag_update_pending[i] = False
            else:
                self.flag_update_pending[i] = True

    def __update_gui_label_fn(self):
        if not self.f:
            text = "(not loaded)"
        elif self.f.filename:
            text = os.path.relpath(self.f.filename, ".")
        else:
            text = "(filename not set)"
        self.label_fn_sky.setText(text)

    def __update_gui_header(self):
        """Updates header controls only"""
        sky = self.f.sparsecube
        self.spinbox_width.setValue(sky.width)
        self.spinbox_height.setValue(sky.height)
        self.spinbox_hrfactor.setValue(sky.hrfactor)
        self.lineEdit_hr_pix_size.setText(str(sky.hr_pix_size))
        self.spinbox_R.setValue(sky.R)
        self.edit_fieldnames.setPlainText(str(sky.fieldnames))
        self.set_flag_header_changed(False)

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
        sky = self.f.sparsecube
        self.flag_valid = self.__update_f_header(sky)

    def __update_f_header(self, sky):
        """Updates headers of a SparseCube objects using contents of the Headers tab"""
        emsg, flag_error = "", False
        ss = ""
        try:
            ss = "fieldnames"
            ff = eval_fieldnames(str(self.edit_fieldnames.toPlainText()))
            sky.fieldnames = ff
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
            self.__update_gui(True)
            flag_emit = True
        except Exception as E:
            flag_error = True
            if ss:
                emsg = "Field '%s': %s" % (ss, str_exc(E))
            else:
                emsg = str_exc(E)
            self.add_log_error(emsg)
        if flag_emit:
            self.__emit_if()
        return not flag_error

    def __update_gui_vis_if_pending(self):
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
            draw_cube_3d(ax, self.f.sparsecube)
            fig.tight_layout()
            self.canvas0.draw()

        except Exception as E:
            self.add_log_error(str_exc(E))
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
            self.obj_square = draw_cube_colors(ax, self.f.sparsecube, vrange, sqx, sqy, flag_scale, method)

            fig.tight_layout()
            self.canvas1.draw()

            self.flag_plot_colors_pending = False
        except Exception as E:
            self.add_log_error(str_exc(E))
            get_python_logger().exception("Could not plot colors")
