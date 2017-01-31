from PyQt4 import QtGui, QtCore

from ..modules.caen895 import CAEN895
from ..modules.caen2718 import v2718

from .caen895 import CAEN_895_Widget

import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

CONTROLLERS = {'v2718': v2718}

MODULES = {'v895': CAEN895}

WIDGETS = {'v895': CAEN_895_Widget}


class BaseaddressDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        super(BaseaddressDialog, self).__init__(parent)

        layout = QtGui.QVBoxLayout(self)

        self.baseSpin = HexSpinBox()
        self.baseSpin.setRange(0x00010000, 0xffff0000)
        self.baseSpin.setSingleStep(0x00010000)
        self.baseSpin.setValue(0x00010000)
        layout.addWidget(self.baseSpin)

        # OK and Cancel buttons
        buttons = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    # get current base address from the dialog
    def baseaddress(self):
        return int(self.baseSpin.value())

    # static method to create the dialog and return (baseaddress, accepted)
    @staticmethod
    def getBaseaddress(parent=None):
        dialog = BaseaddressDialog(parent)
        result = dialog.exec_()
        base_address = dialog.baseaddress()
        return (base_address, result == QtGui.QDialog.Accepted)


class HexSpinBox(QtGui.QDoubleSpinBox):

    def __init__(self, parent=None):
        super(HexSpinBox, self).__init__(parent)

        regex = QtCore.QRegExp('[0-9A-Fa-f]{1,9}')
        regex.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.validator = QtGui.QRegExpValidator(regex, self)
        self.setRange(0, 255)
        self.setDecimals(0)

    def validate(self, text, pos):
        return self.validator.validate(text, pos)

    def valueFromText(self, text):
        return text.toInt(16)[0]

    def textFromValue(self, value):
        return QtCore.QString.number(value, 16).toUpper()


class ModuleSelector(QtGui.QWidget):
    def __init__(self, parent=None):
        super(ModuleSelector, self).__init__(parent=parent)
        self.InitUI()

    def InitUI(self):
        layout = QtGui.QVBoxLayout()

        layout.addWidget(QtGui.QLabel('Controller'))
        self.controllerCombo = QtGui.QComboBox()
        self.controllerCombo.addItems(CONTROLLERS.keys())
        layout.addWidget(self.controllerCombo)

        layout.addWidget(QtGui.QLabel('Module'))
        self.moduleCombo = QtGui.QComboBox()
        self.moduleCombo.addItems(MODULES.keys())
        layout.addWidget(self.moduleCombo)

        layout.addStretch()

        self.okButton = QtGui.QPushButton('Ok')
        layout.addWidget(self.okButton)

        self.setLayout(layout)

    def getController(self):
        controller = self.controllerCombo.currentText()

        return str(controller)

    def getModule(self):
        module = self.moduleCombo.currentText()

        return str(module)


class MainWindow(QtGui.QMainWindow):
    '''
    Mainwindow of CryoRead application.
    '''

    def __init__(self, parent=None):
        '''
        Constructor
        '''
        logger.debug('create MainWindow')
        super(MainWindow, self).__init__(parent)

        self.setWindowTitle('VME Test Suite')
        self.setFocus()

        self.initUI()

    def initUI(self):
        logger.debug('init UI')
        statusbar = self.statusBar()
        statusbar.showMessage('Welcome to VME Test Suite :)')
        # --------------- MenuBar -------------------
        # menubar = self.menuBar()

        # dummy central widget
        widget = ModuleSelector(self)
        widget.okButton.clicked.connect(self.module_selected)
        self.setCentralWidget(widget)

    def sizeHint(self):
        return QtCore.QSize(400, 300)

    def replaceWidget(self, widget):
        msg = 'replace widget {0} with widget {1}'
        logger.debug(msg.format(self.centralWidget(), widget))
        self.centralWidget().hide()
        self.centralWidget().close()
        self.setCentralWidget(widget)

    def module_selected(self):
        widget = self.centralWidget()
        controller = widget.getController()
        module = widget.getModule()

        msg = 'module selected (controller = {0}, module = {1})'
        logger.debug(msg.format(controller, module))

        app = QtGui.QApplication.instance()
        app.initController(controller)
        app.initModule(module)


class VMESuite(QtGui.QApplication):
    '''
    Qt Application class of cryoread.

    Owns basic settings to connect to FADC and temperature server.
    Keeps a reference to the main window and has functions to
    display messages in the sattus bar.
    '''
    def __init__(self, args):
        self.controller = None
        self.module = None

        super(VMESuite, self).__init__(args)
        self.mainWindow = MainWindow()
        self.mainWindow.show()

    def updateStatus(self, status):
        '''
        Display status message in status bar of main window
        '''
        statusbar = self.mainWindow.statusBar()
        statusbar.showMessage(status)

    def initController(self, controller):
        logger.debug('init controller ({0})'.format(controller))

        del self.controller
        self.controller = CONTROLLERS[controller]()

    def initModule(self, module):
        logger.debug('init module ({0})'.format(module))
        base_address, ok = BaseaddressDialog.getBaseaddress()

        logger.debug('base address selected: ({0})'.format(base_address))

        if ok:
            self.module = MODULES[module](self.controller, base_address)
            widget = WIDGETS[module](self.module)
            self.mainWindow.replaceWidget(widget)
        else:
            logger.warning('base address not set correctly')


def main():
    import argparse

    d = """
    VME Test Suite
    --------------------------------------------------------------------------

    Test selected VME Modules.
    """

    parser = argparse.ArgumentParser(description=d)
    parser.add_argument('-v', '--verbosity',
                        type=int,
                        default=40,
                        choices=[10, 20, 30, 40, 50],
                        help='set threshold for messages shown on screen (10 everything, 50 only critical messages)')

    args = parser.parse_args()

    fmt = "%(name)s %(levelname)s: %(message)s"
    level = logging.getLevelName(args.verbosity)
    logging.basicConfig(format=fmt, level=level)

    import sys
    app = VMESuite(sys.argv)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
