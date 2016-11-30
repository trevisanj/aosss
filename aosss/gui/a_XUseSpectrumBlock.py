__all__ = ["XUseSpectrumBlock"]


from PyQt4.QtCore import *
from PyQt4.QtGui import *
from pyfant.gui import *
from pyfant import blocks, collect_doc, module_to_dict, str_exc
import pyfant as pf
from .a_XHelpDialog import *

_CONFIG_OPERATIONS = "/gui/XUseSpectrumBlock/operations"

class XUseSpectrumBlock(XHelpDialog):
    """
    Edit Parameters to apply a SpectrumBlock to each spectrum in a Spectrum List

    Relevant attributes (set on close):
      self.block -- None or SpectrumBlock instance
    """

    def __init__(self, *args):
        XHelpDialog.__init__(self, *args)

        self.previous_operations = pf.get_config().get_item(_CONFIG_OPERATIONS, [])
        self.block = None

        self.setWindowTitle("Transform")

        self.labelHelpTopics.setText("&Available operations")

        self.help_data = collect_doc(blocks.sb, base_class=blocks.base.SpectrumBlock)
        self.comboBox.addItems([x[0] for x in self.help_data])
        ###
        label = QLabel(enc_name_descr("O&peration", "See help below"))
        label.setAlignment(Qt.AlignRight)
        cb = self.cb_operation = QComboBox()
        label.setBuddy(cb)
        cb.setEditable(True)
        cb.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        cb.addItems(self.previous_operations)
        self.grid.addWidget(label, 0, 0)
        self.grid.addWidget(cb, 0, 1)

        place_center(self, 800, 600)


    def accept(self):
        try:
            expr = str(self.cb_operation.currentText())
            block = eval(expr.strip(), {}, module_to_dict(blocks.sb))

            if not isinstance(block, blocks.base.SpectrumBlock):
                raise RuntimeError("Expression does not evaluate to a valid Spectrum Block")

            self.block = block

            # Saves new operation on close (if evaluated successfully)
            if not expr in self.previous_operations:
                self.previous_operations.append(expr)
                self.previous_operations.sort()
                pf.get_config().set_item(_CONFIG_OPERATIONS, self.previous_operations)

            return QDialog.accept(self)
        except Exception as e:
            self.add_log_error(str_exc(e), True)
            return False
