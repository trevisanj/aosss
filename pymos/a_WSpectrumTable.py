"""Widget to edit a FileSky object."""

__all__ = ["WSpectrumTable"]

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
from .a_XScaleSpectrum import *
from .filespectrumlist import *


class WSpectrumTable(WBase):
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
        self.collection = None # SpectrumCollection


        # # Central layout
        lwex = self.centralLayout = QVBoxLayout()
        lwex.setMargin(0)
        self.setLayout(lwex)
        ###
        lwexex = QHBoxLayout()
        lwexex.setMargin(0)
        lwexex.setSpacing(2)
        lwex.addLayout(lwexex)
        ###
        b = keep_ref(QPushButton("Scale..."))
        b.clicked.connect(self.scale_clicked)
        lwexex.addWidget(b)
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
        a = self.twSpectra = QTableWidget()
        lwex.addWidget(a)
        a.setSelectionMode(QAbstractItemView.MultiSelection)
        a.setSelectionBehavior(QAbstractItemView.SelectRows)
        a.setAlternatingRowColors(True)
        a.cellChanged.connect(self.on_twSpectra_cellChanged)
        a.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
        a.setFont(MONO_FONT)
        a.installEventFilter(self)
        a.setContextMenuPolicy(Qt.CustomContextMenu)
        a.customContextMenuRequested.connect(self.on_twSpectra_customContextMenuRequested)

        self.setEnabled(False)  # disabled until load() is called
        style_checkboxes(self)
        self.flag_process_changes = True
        self.add_log("Welcome from %s.__init__()" % (self.__class__.__name__))


    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Interface

    def set_collection(self, x):
        assert isinstance(x, SpectrumCollection)
        self.collection = x
        self.__update_from_f()
        self.setEnabled(True)

    def get_selected_row_indexes(self):
        ii = list(set([index.row() for index in self.twSpectra.selectedIndexes()]))
        return ii

    def update(self):
        """Refreshes the GUI to reflect what is in self.collection"""
        self.__update_from_f()

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Qt override

    def setFocus(self, reason=None):
        """Sets focus to first field. Note: reason is ignored."""
        self.twSpectra.setFocus()

    def eventFilter(self, source, event):
        if event.type() == QEvent.FocusIn:
            # text = random_name()
            # self.__add_log(text)
            pass

        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Delete:
                if source == self.twSpectra:
                    n_deleted = self.__delete_spectra()
                    if n_deleted > 0:
                        self.edited.emit()
        return False

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Slots

    # TODO dialog box to select multiple spectra
    def go_clicked(self):
        print "GO CLICKED\n"*10
        flag_emit = False
        try:
            x, y = self.get_place_spectrum_xy()
            sp = self.choosesp.sp
            if not sp:
                raise RuntimeError("Spectrum not loaded")
            sp.pixel_x, sp.pixel_y = x, y
            self.collection.add_spectrum(sp)
            self.__update_from_f()
            flag_emit = True
        except Exception as E:
            self.add_log_error(str(E), True)
            raise
        if flag_emit:
            self.edited.emit()

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
        sspp = [self.collection.spectra[i] for i in self.get_selected_row_indexes()]
        if len(sspp) > 0:
            plot_spectra(sspp)

    def plot_overlapped_clicked(self):
        sspp = [self.collection.spectra[i] for i in self.get_selected_row_indexes()]
        if len(sspp) > 0:
            plot_spectra_overlapped(sspp)

    def delete_selected(self):
        n = self.__delete_spectra()
        if n > 0:
            self.edited.emit()
        
    def scale_clicked(self):
        if len(self.collection) > 0:
          sp = self.collection.spectra[self.twSpectra.currentRow()]
          
        form = XScaleSpectrum()
        form.set_spectrum(sp)
        if form.exec_():
            k = form.factor()
            if k != 1:
                sp.y *= k
                self.__update_from_f()
                self.edited.emit()

    def on_twSpectra_cellChanged(self, row, column):
        if self.flag_process_changes:
            flag_emit = False
            text = None
            item = self.twSpectra.item(row, column)
            name = self.get_tw_header(column)
            try:
                value = str(item.text())
                # Tries to convert to float, otherwise stores as string
                try:
                    value = float(value)
                except:
                    pass

                # Certain fields must evaluate to integer because they are pixel positions
                if name in ("PIXEL-X", "PIXEL-Y", "Z-START"):
                    value = int(value)

                self.collection.spectra[row].more_headers[name] = value

                flag_emit = True
                # replaces edited text with eventually cleaner version, e.g. decimals from integers are discarded
                item.setText(str(value))

            except Exception as E:
                # restores original value
                item.setText(str(self.collection.spectra[row].more_headers.get(name)))

                self.add_log_error(str(E), True)
                raise

            if flag_emit:
                self.edited.emit()

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Internal gear

    def get_tw_header(self, column):
        return str(self.twSpectra.horizontalHeaderItem(column).text())

    def __update_from_f(self):
        self.flag_process_changes = False
        try:
            spectra = self.collection.spectra
            t = self.twSpectra
            n = len(spectra)

            FIXED = ["spectrum"]
            more_headers = self.collection.fieldnames
            all_headers = more_headers+FIXED
            nc = len(all_headers)
            ResetTableWidget(t, n, nc)
            t.setHorizontalHeaderLabels(all_headers)
            i = 0
            for sp in spectra:
                j = 0

                # Spectrum.more_headers columns
                for h in more_headers:
                    twi = QTableWidgetItem(str(sp.more_headers.get(h)))
                    t.setItem(i, j, twi)
                    j += 1

                # Spectrum self-generated report
                twi = QTableWidgetItem(sp.one_liner_str())
                twi.setFlags(twi.flags() & ~Qt.ItemIsEditable)
                t.setItem(i, j, twi)
                j += 1

                i += 1

            t.resizeColumnsToContents()

        finally:
            self.flag_process_changes = True

    def __delete_spectra(self):
        ii = self.get_selected_row_indexes()
        if len(ii) > 0:
            self.collection.delete_spectra(ii)
            self.__update_from_f()

        return len(ii)
