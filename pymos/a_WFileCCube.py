"""Widget to edit a FileCCube object."""

__all__ = ["WFileCCube"]

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from pyfant.gui.guiaux import *
from pyfant import random_name
import random
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT # as NavigationToolbar2QT
import matplotlib.pyplot as plt
import numpy as np
from itertools import product, combinations
from fileccube import *
from a_WChooseSpectrum import *


class WFileCCube(QWidget):
    """
    FileCCube editor widget.

    Arguments:
      parent=None
    """

    # Emitted whenever any value changes
    edited = pyqtSignal()

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        # Whether all the values in the fields are valid or not
        self.flag_valid = False
        # Internal flag to prevent taking action when some field is updated programatically
        self.flag_process_changes = False
        self.f = None # FileCCube object


        # # Central layout
        la = self.centralLayout = QVBoxLayout()
        la.setMargin(0)
        self.setLayout(la)

        # ## Vertical splitter with (main area) / (error area)
        sp = self.splitter = QSplitter(Qt.Vertical)
        la.addWidget(sp)


        # ### Horizontal splitter occupying main area: (options area) | (plot area)
        sp2 = self.splitter2 = QSplitter(Qt.Horizontal)

        # #### Scroll area occupying left of horizontal splitter
        sa = self.c33441 = QScrollArea()
        sa.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        sa.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Widget that will be handled by the scrollable area
        scrw = self.scrollWidget = QWidget()
        sa.setWidget(self.scrollWidget)
        sa.setWidgetResizable(True)
#        la.addWidget(w)

        lscrw = QVBoxLayout()
        scrw.setLayout(lscrw)

        alabel = self.c39efj = QLabel("Place spectrum")
        lscrw.addWidget(alabel)


        # Form layout
        lg = self.formLayout = QGridLayout()
        lscrw.addLayout(lg)
        lg.setMargin(0)
        lg.setVerticalSpacing(4)
        lg.setHorizontalSpacing(5)
        lscrw.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # field map: [(label widget, edit widget, field name, short description, long description), ...]
        pp = self._map = []
        #####
        x = self.label_sp = QLabel()
        y = self.choosesp = WChooseSpectrum()
        y.installEventFilter(self)
        y.edited.connect(self.on_edited)
        # y.setValidator(QIntValidator())
        x.setBuddy(y)
        pp.append((x, y, "&spectrum", ".dat, .fits ...", ""))
        #####
        x = self.label_x = QLabel()
        y = self.lineEdit_x = QLineEdit()
        y.installEventFilter(self)
        y.textEdited.connect(self.on_edited)
        # y.setValidator(QIntValidator())
        x.setBuddy(y)
        pp.append((x, y, "&x", "x-coordinate<br>(pixels; 0-based)", ""))
        #####
        x = self.label_y = QLabel()
        y = self.lineEdit_y = QLineEdit()
        y.installEventFilter(self)
        y.textEdited.connect(self.on_edited)
        # y.setValidator(QIntValidator())
        x.setBuddy(y)
        pp.append((x, y, "&y", "y-coordinate", ""))
        #####
        x = self.label_fwhm = QLabel()
        y = self.lineEdit_fwhm = QLineEdit()
        y.installEventFilter(self)
        y.textEdited.connect(self.on_edited)
        y.setValidator(QDoubleValidator(0, 10, 5))
        x.setBuddy(y)
        pp.append((x, y, "f&whm", "full width at<br>half-maximum (pixels)", ""))



        for i, (label, edit, name, short_descr, long_descr) in enumerate(pp):
            # label.setStyleSheet("QLabel {text-align: right}")
            assert isinstance(label, QLabel)
            label.setText(enc_name_descr(name, short_descr))
            label.setAlignment(Qt.AlignRight)
            lg.addWidget(label, i, 0)
            lg.addWidget(edit, i, 1)
            label.setToolTip(long_descr)
            edit.setToolTip(long_descr)


        lgo = QHBoxLayout()
        lscrw.addLayout(lgo)
        lgo.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        bgo = self.c23983s = QPushButton("Go")
        lgo.addWidget(bgo)
        bgo.clicked.connect(self.go_clicked)


        lscrw.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))




        # #### Tabbed widget occupying right of horizontal splitter
        tt = self.tabWidget = QTabWidget(self)
        la.addWidget(tt)
        tt.setFont(MONO_FONT)

        # ##### Tab containing 3D plot representation
        w0 = self.c27272 = QWidget()
        tt.addTab(w0, "plot 3D")
        # http://stackoverflow.com/questions/12459811
        self.figure0, self.canvas0, self.lfig0 = get_matplotlib_layout(w0)
        # lscrw.addLayout(lfig)

        # ##### Colors tab
        w1 = self.c27272 = QWidget()
        tt.addTab(w1, "colors")
        self.figure1, self.canvas1, self.lfig1 = get_matplotlib_layout(w1)


        sp2.addWidget(sa)
        sp2.addWidget(tt)



        # ### Second widget of vertical splitter
        # layout containing description area and a error label
        wlu = QWidget()
        lu = QVBoxLayout(wlu)
        lu.setMargin(0)
        lu.setSpacing(1)
        # this was taking unnecessary space
        # x = self.c23862 = QLabel("<b>Help</b>")
        # lu.addWidget(x)
        # x = self.textEditDescr = QTextEdit(self)
        # x.setReadOnly(True)
        # x.setStyleSheet("QTextEdit {color: %s}" % COLOR_DESCR)
        # lu.addWidget(x)
        x = self.c23862 = QLabel("<b>Errors</b>")
        lu.addWidget(x)
        x = self.labelError = QLabel(self)
        x.setStyleSheet("QLabel {color: %s}" % COLOR_ERROR)
        lu.addWidget(self.labelError)


        sp.addWidget(sp2)
        sp.addWidget(wlu)


        self.setEnabled(False)  # disabled until load() is called
        style_checkboxes(self)
        self.flag_process_changes = True

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Interface

    def load(self, x):
        assert isinstance(x, FileCCube)
        self.f = x
        self.__update_from_f()
        # this is called to perform file validation upon loading
        # TODO probably not like this
        self.__update_f()
        self.setEnabled(True)

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Qt override

    def setFocus(self, reason=None):
        """Sets focus to first field. Note: reason is ignored."""
        # TODO self.lineEdit_titrav.setFocus()

    def eventFilter(self, obj_focused, event):
        if event.type() == QEvent.FocusIn:
            text = random_name()
            # for label, obj, name, short_descr, color, long_descr in self._map:
            #     if obj_focused == obj:
            #         text = "%s<br><br>%s" % \
            #                (enc_name(name.replace("&", ""), color), long_descr)
            #         break

            self.__set_descr_text(text)
        return False

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Slots

    def on_edited(self):
        if self.flag_process_changes:
            self.__update_f()
            self.edited.emit()

    def go_clicked(self):
        print "GO CLICKED\n"*10

    def sp_double_click(self):
        print "CHOOSE FILE....."

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Internal gear

    def __update_from_f(self):
        self.flag_process_changes = False
        try:
            o = self.f
            self.plot_spectra()
            # self.lineEdit_titrav.setText(o.titrav)
            # self.lineEdit_teff.setText(str(o.teff))
            # self.lineEdit_glog.setText(str(o.glog))
            # self.lineEdit_asalog.setText(str(o.asalog))
            # self.lineEdit_vvt.setText(str(o.vvt[0]))
            # self.lineEdit_nhe.setText(str(o.nhe))
            # self.checkBox_ptdisk.setChecked(o.ptdisk)
            # self.lineEdit_mu.setText(str(o.mu))
            # self.lineEdit_flprefix.setText(o.flprefix)
            # self.lineEdit_pas.setText(str(o.pas))
            # self.lineEdit_llzero.setText(str(o.llzero))
            # self.lineEdit_llfin.setText(str(o.llfin))
            # self.lineEdit_aint.setText(str(o.aint))
            # self.lineEdit_fwhm.setText(str(o.fwhm))
        finally:
            self.flag_process_changes = True

    def __set_error_text(self, x):
        """Sets text of labelError."""
        self.labelError.setText(x)

    def __set_descr_text(self, x):
        """Sets text of labelDescr."""
        self.textEditDescr.setText(x)

    def __update_f(self):
        o = self.f
        emsg, flag_error = "", False
        ss = ""
        try:
            pass
            # ss = "titrav"
            # o.titrav = str(self.lineEdit_titrav.text())
            # ss = "teff"
            # o.teff = float(self.lineEdit_teff.text())
            # ss = "glog"
            # o.glog = float(self.lineEdit_glog.text())
            # ss = "asalog"
            # o.asalog = float(self.lineEdit_asalog.text())
            # o.afstar = o.asalog  # makes afstar match asalog
            # ss = "vvt"
            # temp = float(self.lineEdit_vvt.text())
            # if temp > 900:
            #     raise RuntimeError("Not prepared for depth-variable velocity "
            #      "of microturbulence (maximum allowed: 900)")
            # o.vvt = [temp]
            # ss = "nhe"
            # o.nhe = float(self.lineEdit_nhe.text())
            # ss = "ptdisk"
            # o.ptdisk = self.checkBox_ptdisk.isChecked()
            # ss = "mu"
            # o.mu = float(self.lineEdit_mu.text())
            # ss = "flprefix"
            # o.flprefix = str(self.lineEdit_flprefix.text())
            # ss = "pas"
            # o.pas = float(self.lineEdit_pas.text())
            # ss = "llzero"
            # o.llzero = float(self.lineEdit_llzero.text())
            # ss = "llfin"
            # o.llfin = float(self.lineEdit_llfin.text())
            # ss = "aint"
            # o.aint = float(self.lineEdit_aint.text())
            # ss = "fwhm"
            # o.fwhm = float(self.lineEdit_fwhm.text())
            #
            # # Some error checks
            # ss = ""
            # if o.llzero >= o.llfin:
            #     raise RuntimeError("llzero must be lower than llfin!")
            # if not (-1 <= o.mu <= 1):
            #     raise RuntimeError("mu must be between -1 and 1!")
        except Exception as E:
            flag_error = True
            if ss:
                emsg = "Field \"%s\": %s" % (ss, str(E))
            else:
                emsg = str(E)
                # ShowError(str(E))
        self.flag_valid = not flag_error
        self.__set_error_text(emsg)


    def plot_spectra(self):
        # self.clear_markers()
        if self.f is not None:
            fig = self.figure0
            fig.clear()
            ax = fig.gca(projection='3d')
            _plot_spectra(ax, self.f.ccube)
            fig.tight_layout()


            fig = self.figure1
            fig.clear()
            ax = fig.gca()
            plot_colors(ax, self.f.ccube)

            fig.tight_layout()



def _plot_spectra(ax, ccube):
    """

    data cube            mapped to 3D axis
    X pixel coordinate   x
    Y pixel coordinate   z
    Z wavelength         y
    """


    assert isinstance(ccube, CompassCube)
    data = ccube.hdu.data
    nlambda, nY, nX = data.shape
    scale = 1/np.max(data.flatten())
    _x = np.ones(nlambda)
    _y = ccube.wavelength
    _z = np.ones(nlambda)
    dlambda = _y[1]-_y[0]
    r0 = [-.5, nX + .5]
    r1 = [_y[0] - dlambda / 2, _y[-1] + dlambda / 2]
    r2 = [-.5, nY + .5]


    PAR = {"color": "y", "alpha": 0.3}
    def draw_line(*args):
        ax.plot3D(*args, **PAR)



    # draw cube
    for s, e in combinations(np.array(list(product(r0, r1, r2))), 2):
        if np.sum(s == e) == 2:
        # if np.sum(np.abs(s - e)) == r[1] - r[0]:
            draw_line(*zip(s, e))


    # draws grids
    for i in range(nX+1):
        draw_line([i-.5]*2, [r1[0]]*2, r2)
        draw_line([i-.5]*2, [r1[1]]*2, r2)
    for i in range(nY + 1):
        draw_line(r0, [r1[0]]*2, [i-.5]* 2)
        draw_line(r0, [r1[1]]*2, [i-.5]* 2)


    for i in range(nX):
        for j in range(nY):
            Yi = j+1
            flux0 = data[:, j, i]
            if np.any(flux0 > 0):
                flux1 = flux0 * scale - Yi + .5
                ax.plot(_x*(i+1), _y, flux1+_z*(j+1), label='a', color='k')

    # ax.set_aspect("equal")
    ax.set_xlabel("x (pixel)")
    ax.set_ylabel('wavelength ($\AA$)')  # ax.set_ylabel('wavelength ($\AA$)')
    ax.set_zlabel('y (pixel)')
    # ax.set_zlabel('?')
    # plt.show()


