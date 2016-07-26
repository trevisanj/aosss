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


class XScaleSpectrum(XLogMainWindow):
    """Application template with file operations in two tabs: (application area) and (log)"""

    def __init__(self, parent=None, file_main=None, file_abonds=None):
        def keep_ref(obj):
            self.__refs.append(obj)
            return obj

        XLogMainWindow.__init__(self, parent)
        self.__refs = []


        # # Central layout
        ##################
        cw = self.centralWidget = QWidget()
        self.setCentralWidget(cw)
        lantanide = self.centralLayout = QVBoxLayout(cw)
        lantanide.setMargin(1)
        
        sw = self.scale_widget = WScaleSpectrum(self)
        lantanide.addWidget(sw)
        
        lokc = QHBoxLayout()
        lantanide.addLayout(lokc)
        ###
        lokc.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        ###
        b = keep_ref(QPushButton("OK"))
        b.clicked.connect(self.ok_clicked)
        lokc.addWidget(b)
        ###
        b = keep_ref(QPushButton("Cancel"))
        b.clicked.connect(self.cancel_clicked)
        lokc.addWidget(b)
        

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # Interface

    def set_spectrum(self, sp):
        self.scale_widget.set_spectrum(sp)


    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # Slots

    def ok_clicked(self):
        print "entao ok ne"

    def cancel_clicked(self):
        print "entao cancel ne"

