from PyQt4 import QtGui

import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class CAEN_895_Widget(QtGui.QWidget):
    '''
    classdocs
    '''

    def __init__(self, v895, parent=None):
        '''
        Constructor
        '''
        super(CAEN_895_Widget, self).__init__(parent)
        self.setWindowTitle('CAEN v895 - 16 Channel LED')

        self.v895 = v895

        self.initUI()

    def initUI(self):
        channelGroup = QtGui.QGroupBox('Channels')

        channelForm = QtGui.QFormLayout()

        self.thresholdBoxes = []
        self.enableBoxes = []

        for i in range(16):
            thrBox = QtGui.QSpinBox()
            thrBox.setRange(1, 255)
            thrBox.setValue(1)
            thrBox.setToolTip('threshold value in mV (1-255)')
            self.thresholdBoxes.append(thrBox)

            enBox = QtGui.QCheckBox()
            enBox.setToolTip('check to enable channel')
            self.enableBoxes.append(enBox)

            lo = QtGui.QHBoxLayout()
            lo.addWidget(thrBox)
            lo.addWidget(enBox)

            channelForm.addRow('Channel {0}'.format(i), lo)

        channelGroup.setLayout(channelForm)

        widthGroup = QtGui.QGroupBox('Output Width')

        widthForm = QtGui.QFormLayout()

        self.width1Spin = QtGui.QSpinBox()
        self.width1Spin.setRange(0, 255)
        self.width1Spin.setToolTip('width of output pulse for channels 0-7')
        self.width2Spin = QtGui.QSpinBox()
        self.width2Spin.setRange(0, 255)
        self.width2Spin.setToolTip('width of output pulse for channels 8-15')

        widthForm.addRow('Channels 0-7', self.width1Spin)
        widthForm.addRow('Channels 8-15', self.width2Spin)

        widthGroup.setLayout(widthForm)

        majGroup = QtGui.QGroupBox('Majority')

        majForm = QtGui.QFormLayout()

        self.majSpin = QtGui.QSpinBox()
        self.majSpin.setRange(0, 20)
        self.majSpin.setToolTip('number of channels which have to trigger simultaneously to generate output on "Majority Out"')
        majForm.addRow('Majority', self.majSpin)

        majGroup.setLayout(majForm)

        self.testButton = QtGui.QPushButton('Send')
        self.testButton.setToolTip('generate test pulse on all outputs')
        self.testButton.clicked.connect(self.sendTestpulse)

        self.okButton = QtGui.QPushButton('Ok')
        self.okButton.setToolTip('write settings to module')
        self.okButton.clicked.connect(self.pushSettings)

        # putting everything together
        layout = QtGui.QHBoxLayout()
        layout.addWidget(channelGroup)

        lo_right = QtGui.QVBoxLayout()
        lo_right.addWidget(widthGroup)
        lo_right.addWidget(majGroup)
        lo_right.addStretch()
        lo_right.addWidget(self.testButton)
        lo_right.addWidget(self.okButton)

        layout.addLayout(lo_right)
        layout.setSizeConstraint(QtGui.QLayout.SetFixedSize)

        self.setLayout(layout)

    def sendTestpulse(self):
        logger.debug('sending test pulse')
        self.v895.sendTestpulse()

    def pushSettings(self):
        channelList = []

        for i, z in enumerate(zip(self.thresholdBoxes, self.enableBoxes)):
            if z[1].isChecked():
                channelList.append(i)
                thr = z[0].value()
                msg = 'channel {0} is enabled, threshold: {1}'
                logger.debug(msg.format(i, thr))
                self.v895.setThreshold(i, thr)

        self.v895.enableChannels(channelList)

        width = self.width1Spin.value()
        logger.debug('width group 1 is {0}'.format(width))
        self.v895.setOutputWidth(1, width)

        width = self.width2Spin.value()
        logger.debug('width group 2 is {0}'.format(width))
        self.v895.setOutputWidth(2, width)

        maj = self.majSpin.value()
        logger.debug('set majority to {0}'.format(maj))
        self.v895.setMajority(maj)
