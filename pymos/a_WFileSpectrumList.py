"""Widget to edit a FileSpectrumList object."""

__all__ = ["WFileSpectrumList"]

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from pyfant.gui import *
from pyfant import *
import os
import copy
from pymos import *
import traceback as tb

class WFileSpectrumList(WBase):
    """
    FileSpectrumList editor widget.

    Arguments:
      parent=None
    """

    def __init__(self, parent):
        WBase.__init__(self, parent)

        def keep_ref(obj):
            self._refs.append(obj)
            return obj

        # Whether __update_f() went ok
        self.flag_valid = False
        # Internal flag to prevent taking action when some field is updated programatically
        self.flag_process_changes = False
        # Whether there is sth in yellow background in the Headers tab
        self.flag_header_changed = False
        self.f = None # FileSpectrumList object
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
        w = self.label_fn = QLabel()
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
        alabel = keep_ref(QLabel("<b>Add spectrum</b>"))
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
        b.clicked.connect(self.add_spectrum_clicked)

        # ##### Existing Spectra area
        wex = QWidget()
        lwex = QVBoxLayout(wex)
        lwex.setMargin(3)
        ###
        lwex.addWidget(keep_ref(QLabel("<b>Existing spectra</b>")))
        ###
        lwexex = QHBoxLayout()
        lwexex.setMargin(0)
        lwexex.setSpacing(2)
        lwex.addLayout(lwexex)
        ###
        lwexex.addWidget(keep_ref(QLabel("With selected:")))
        ###
        b = keep_ref(QPushButton("Plot &stacked"))
        b.clicked.connect(self.plot_stacked_clicked)
        lwexex.addWidget(b)
        ###
        b = keep_ref(QPushButton("Plot &overlapped"))
        b.clicked.connect(self.plot_overlapped_clicked)
        lwexex.addWidget(b)
        ###
        b = keep_ref(QPushButton("Delete"))
        b.clicked.connect(self.delete_selected)
        lwexex.addWidget(b)
        ###
        lwexex.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        ###
        b = keep_ref(QPushButton("Import..."))
        b.clicked.connect(self.import_clicked)
        lwexex.addWidget(b)
        ###
        a = self.twSpectra = QTableWidget()
        lwex.addWidget(a)
        a.setSelectionMode(QAbstractItemView.MultiSelection)
        a.setSelectionBehavior(QAbstractItemView.SelectRows)
        a.setAlternatingRowColors(True)
        #a.currentCellChanged.connect(self.on_tableWidget_currentCellChanged)
        a.setEditTriggers(QAbstractItemView.NoEditTriggers)
        a.setFont(MONO_FONT)
        a.installEventFilter(self)
        a.setContextMenuPolicy(Qt.CustomContextMenu)
        a.customContextMenuRequested.connect(self.on_twSpectra_customContextMenuRequested)

        # ##### Finally...
        spp.addWidget(sa0)
        spp.addWidget(wex)

        # #### Headers tab
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

        ###
        b = keep_ref(QPushButton("Collect field names"))
        b.clicked.connect(self.on_collect_fieldnames)
        lscrw.addWidget(b)

        # Form layout
        lg = keep_ref(QGridLayout())
        lg.setMargin(0)
        lg.setVerticalSpacing(4)
        lg.setHorizontalSpacing(5)
        lscrw.addLayout(lg)
        ###
        lscrw.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # field map: [(label widget, edit widget, field name, short description, long description, f_from_f, f_from_edit), ...]
        pp = self._map1 = []


        ###
        x = keep_ref(QLabel())
        y = self.edit_fieldnames = QPlainTextEdit()
        y.textChanged.connect(self.on_header_edited)
        x.setBuddy(y)
        pp.append((x, y, "&Field names", "'header' information for each spectrum", "", lambda: self.f.splist.fieldnames,
                   lambda: self.edit_fieldnames.toPlainText()))
        ###

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
        la = keep_ref(QLabel("<b>Data manipulation</b>"))
        lwset.addWidget(la)
        ###
        b = keep_ref(QPushButton("&Crop in new window..."))
        lwset.addWidget(b)
        b.clicked.connect(self.crop_clicked)
        ###
        b = keep_ref(QPushButton("Add &noise..."))
        lwset.addWidget(b)
        b.clicked.connect(self.add_noise_clicked)
        ###
        b = keep_ref(QPushButton("&Upper envelopes"))
        lwset.addWidget(b)
        b.clicked.connect(self.rubberband_clicked)
        ###
        b = keep_ref(QPushButton("&Extract continua"))
        lwset.addWidget(b)
        b.clicked.connect(self.extract_continua_clicked)
        ###
        b = keep_ref(QPushButton("&Standard deviation"))
        lwset.addWidget(b)
        b.clicked.connect(self.std_clicked)
        ###
        b = keep_ref(QPushButton("S&NR"))
        lwset.addWidget(b)
        b.clicked.connect(self.snr_clicked)
        ###
        la = keep_ref(QLabel("<b>Export</b>"))
        lwset.addWidget(la)
        ###
        b = keep_ref(QPushButton("E&xport plain text..."))
        lwset.addWidget(b)
        b.clicked.connect(self.export_plain_text_clicked)
        ###
        lwset.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding    ))


        # ### Tabbed widget occupying right of horizontal splitter
        tt1 = self.tabWidgetVis = QTabWidget(self)
        tt1.setFont(MONO_FONT)
        tt1.currentChanged.connect(self.current_tab_changed_vis)

        # #### Tab containing 3D plot representation
        w0 = keep_ref(QWidget())
        tt1.addTab(w0, "&P")
        # #### Colors tab
        w1 = keep_ref(QWidget())
        tt1.addTab(w1, "&Q")

        # ### Finally ...
        sp2.addWidget(wfilett0)
        sp2.addWidget(tt1)


        self.setEnabled(False)  # disabled until load() is called
        style_checkboxes(self)
        self.flag_process_changes = True
        self.add_log("Welcome from %s.__init__()" % (self.__class__.__name__))


    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Interface

    def load(self, x):
        assert isinstance(x, FileSpectrumList)
        self.f = x
        self.__update_from_f(True)

        self.setEnabled(True)

    def get_selected_row_indexes(self):
        ii = list(set([index.row() for index in self.twSpectra.selectedIndexes()]))
        return ii

    def get_selected_spectra(self):
        sspp = [self.f.splist.spectra[i] for i in self.get_selected_row_indexes()]
        return sspp

    def update_splist_headers(self, splist):
        """Updates headers of a SpectrumList objects using contents of the Headers tab"""
        emsg, flag_error = "", False
        ss = ""
        flag_emit = False
        try:
            ss = "fieldnames"
            ff = eval_fieldnames(str(self.edit_fieldnames.toPlainText()))
            splist.fieldnames = ff
            self.__update_from_f(True)
            flag_emit = True
        except Exception as E:
            flag_error = True
            if ss:
                emsg = "Field '%s': %s" % (ss, str(E))
            else:
                emsg = str(E)
            self.add_log_error(emsg)
        if flag_emit:
            self.__emit_if()
        return not flag_error

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Qt override

    def setFocus(self, reason=None):
        """Sets focus to first field. Note: reason is ignored."""

    def eventFilter(self, source, event):
        if event.type() == QEvent.FocusIn:
            # text = random_name()
            # self.__add_log(text)
            pass

        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Delete:
                if source == self.twSpectra:
                    n_deleted = self.__delete_spectra()
        return False

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Slots

    def on_colors_setup_edited(self):
        if self.flag_process_changes:
            pass
            # self.flag_plot_colors_pending = True

    def on_header_edited(self):
        if self.flag_process_changes:
            sth = False
            sndr = self.sender()
            for _, edit, _, _, _, f_from_f, f_from_edit in self._map1:
                changed = f_from_f() != f_from_edit()
                sth = sth or changed
                if edit == sndr:
                    _style_widget(self.sender(), changed)
            self.set_flag_header_changed(sth)




    def add_spectrum_clicked(self):
        flag_emit = False
        try:
            sp = self.choosesp.sp
            if not sp:
                raise RuntimeError("Spectrum not loaded")
            self.f.splist.add_spectrum(sp)
            self.__update_from_f()
            flag_emit = True
        except Exception as E:
            self.add_log_error(str(E), True)
            raise
        if flag_emit:
            self.edited.emit()

    def import_clicked(self):
        flag_emit = False
        try:
            sp = self.choosesp.sp
            if not sp:
                raise RuntimeError("Spectrum not loaded")
            self.f.splist.add_spectrum(sp)
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
        if self.update_splist_headers(self.f.splist):
            self.__update_from_f(True)

    def current_tab_changed_vis(self):
        pass
        # if self.flag_plot_colors_pending:
        #     self.plot_colors()

    def current_tab_changed_options(self):
        pass

    def crop_clicked(self):
        try:
            splist = self.f.splist
            specs = (("wavelength_range", {"value": "[%g, %g]" % (splist.wavelength[0], splist.wavelength[-1])}),)
            form = XParametersEditor(specs=specs, title="Add Gaussian noise")
            while True:
                r = form.exec_()
                if not r:
                    break
                kk = form.GetKwargs()
                s = ""
                try:
                    s = "wavelength_range"
                    lambda0, lambda1 = eval(kk["wavelength_range"])
                except Exception as E:
                    self.add_log_error("Failed evaluating %s: %s: %s" % (s, E.__class__.__name__, str(E)), True)
                    continue

                # Works with clone, then replaces original, to ensure atomic operation
                clone = copy.deepcopy(self.f)
                clone.filename = None
                try:
                    clone.splist.crop(lambda0, lambda1)
                except Exception as E:
                    self.add_log_error("Crop operation failed: %s: %s" % (E.__class__.__name__, str(E)), True)
                    continue

                self.__new_window(clone)
                break

        except Exception as E:
            self.add_log_error("Crop failed: %s" % str(E), True)
            raise

    def rubberband_clicked(self):
        self.__use_sblock(Rubberband(flag_upper=True))

    def add_noise_clicked(self):
        specs = (("std", {"labelText": "Noise standard deviation", "value": 1.}),)
        form = XParametersEditor(specs=specs, title="Select sub-range")
        if form.exec_():
            block = AddNoise(**form.GetKwargs())
            self.__use_sblock(block)

    def extract_continua_clicked(self):
        self.__use_slblock(ExtractContinua())

    def std_clicked(self):
        self.__use_slblock(MergeDown(np.std))

    def snr_clicked(self):
        self.__use_slblock(SNR())

    def on_twSpectra_customContextMenuRequested(self, position):
        """Mounts, shows popupmenu for the tableWidget control, and takes action."""
        menu = QMenu()
        actions = []
        actions.append(menu.addAction("Delete selected (Del)"))
        action = menu.exec_(self.twSpectra.mapToGlobal(position))
        if action is not None:
            idx = actions.index(action)
            if idx == 0:
                self.__delete_spectra()

    def plot_stacked_clicked(self):
        sspp = self.get_selected_spectra()
        if len(sspp) > 0:
            plot_spectra(sspp)

    def plot_overlapped_clicked(self):
        sspp = self.get_selected_spectra()
        if len(sspp) > 0:
            plot_spectra_overlapped(sspp)

    def delete_selected(self):
        self.__delete_spectra()

    def export_plain_text_clicked(self):
        print "EXPORT PLAIN TEXT LATER ..."

    def on_collect_fieldnames(self):
        # TODO confirmation

        self.edit_fieldnames.setPlainText(str(self.f.splist.collect_fieldnames()))
#        self.__update_from_f(True)

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Internal gear
    
    def __emit_if(self):
       if self.flag_process_changes:
           self.edited.emit()

    def __update_from_f(self, flag_headers=False):
        """

          flag_headers -- resets header widgets as well
        """
        self.flag_process_changes = False
        try:
            self.update_label_fn()

            splist = self.f.splist
            assert isinstance(splist, SpectrumList)
            t = self.twSpectra
            n = len(splist.spectra)
            FIXED = ["spectrum"]
            more_headers = splist.fieldnames
#            print "FIXED", fixed
#            print "more_headers", more_headers
#            print "fieldnames", splist.fieldnames
#            print "FINDME43"
            all_headers = FIXED+more_headers
            nc = len(all_headers)
            ResetTableWidget(t, n, nc)
            t.setHorizontalHeaderLabels(all_headers)
            i = 0
            for sp in self.f.splist.spectra:
                twi= QTableWidgetItem(sp.one_liner_str())
                t.setItem(i, 0, twi)

                for j, h in enumerate(more_headers):
                    twi = QTableWidgetItem(str(sp.more_headers.get(h, "xuxuxu-xaxaxa")))
                    t.setItem(i, j+1, twi)

                i += 1
            t.resizeColumnsToContents()

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
        self.label_fn.setText(text)

    def __update_from_f_headers(self):
        """Updates header controls only"""
        splist = self.f.splist
        self.edit_fieldnames.setPlainText(str(splist.fieldnames))
        self.set_flag_header_changed(False)

    def add_log_error(self, x, flag_also_show=False):
        """Delegates to parent form"""
        self.parent_form.add_log_error(x, flag_also_show)

    def add_log(self, x, flag_also_show=False):
        """Delegates to parent form"""
        self.parent_form.add_log(x, flag_also_show)

    def set_flag_header_changed(self, flag):
        self.button_apply.setEnabled(flag)
        self.button_revert.setEnabled(flag)
        self.flag_header_changed = flag
        if not flag:
            # If not changed, removes all eventual yellows
            for _, edit, _, _, _, _, _ in self._map1:
                _style_widget(edit, False)

    def __update_f(self):
        self.flag_valid = self.update_splist_headers(self.f.splist)

    def __delete_spectra(self):
        ii = self.get_selected_row_indexes()
        if len(ii) > 0:
            self.f.splist.delete_spectra(ii)
            self.__update_from_f()
            self.__emit_if()

        return len(ii)


    def __new_window(self, clone):
        """Opens new FileSky in new window"""
        form1 = self.keep_ref(self.parent_form.__class__())
        form1.load(clone)
        form1.show()


    def __use_sblock(self, block):
        """Uses block and opens result in new window"""

        # Does not touch the original self.f
        clone = copy.deepcopy(self.f)
        clone.filename = None
        slblock = UseSBlock()
        for i, sp in enumerate(clone.splist.spectra):
            clone.splist.spectra[i] = block.use(sp)
        self.__new_window(clone)


    def __use_slblock(self, block):
        """Uses block and opens result in new window"""
        # Here not cloning current spectrum list, but trusting the block
        block.flag_copy_wavelength = True
        output = block.use(self.f.splist)
        f = self.__new_from_existing()
        f.splist = output
        self.__new_window(f)

    def __new_from_existing(self):
        """Creates new FileSpectrumList from existing one"""
        f = FileSpectrumList()
        return f


def _style_widget(w, flag_changed):
    """(Paints background yellow)/(removes stylesheet)"""
    w.setStyleSheet("QWidget {background-color: #FFFF00}" if flag_changed else "")
