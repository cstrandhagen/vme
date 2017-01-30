import numpy as np

import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


THRESHOLD = [0x00, 0x02, 0x04, 0x06, 0x08, 0x0A, 0x0C, 0x0E,
             0x10, 0x12, 0x14, 0x16, 0x18, 0x1A, 0x1C, 0x1E]

OUTPUTWIDTH_1 = 0x40
OUTPUTWIDTH_2 = 0x42

MAJORITY = 0x48

INHIBIT = 0x4A

TEST_PULSE = 0x4C

FIXED_CODE = 0xFA
MODULE_TYPE = 0xFC
VERSION = 0xFE


def majority(maj):
    return int(round((maj * 50 - 25) / 4.))


class CAEN895(object):
    '''
    Implements the functionality of the CAEN895 LED.
    '''
    def __init__(self, vme, base_address):
        self.vme = vme
        self.base_address = base_address

    def getModuleID(self):
        logger.debug('get module ID')
        return self.vme.singleReadD16(self.base_address + FIXED_CODE)

    def getModuleType(self):
        return self.vme.singleReadD16(self.base_address + MODULE_TYPE)

    def getVersion(self):
        return self.vme.singleReadD16(self.base_address + VERSION)

    def setThreshold(self, channel, threshold):
        '''
        Set threshold of specified channel.

        Parameters
        ----------
        channel : int
            Channel number (between 0 and 15)
        threshold : int
            Threshold in mV (between 1 and 255)
        '''
        if (channel < 0) | (channel > 15):
            raise ValueError('channel must be between 0 and 15')

        if (threshold < 1) | (threshold > 255):
            raise ValueError('threshold must be between 1 and 255')

        self.vme.singleWriteD16(self.base_address + THRESHOLD[channel],
                                threshold)

    def enableChannels(self, channel_list):
        '''
        Enable channels specified in channel_list.

        Parameters
        ----------
        channel_list : list
            List of channel numbers (between 0 and 15) to enable.
            All other channels are disabled.
        '''
        mask = 16 * [False]

        for channel in channel_list:
            if (channel < 0) | (channel > 15):
                raise ValueError('channel must be between 0 and 15')

            mask[channel] = True

        mask = int(''.join([str(int(el)) for el in mask]), 2)

        self.vme.singleWriteD16(self.base_address + INHIBIT, mask)

    def setOutputWidth(self, group, width):
        '''
        Set width of output pulses for given channel group.

        Parameters
        ----------
        group : int
            Channel group (1: channels 0-7, 2: channels 8-15).
        width : int
            Output pulse width from 0 (= 5ns) to 255 (= 40 ns).
        '''
        if group == 1:
            address = self.base_address + OUTPUTWIDTH_1
        elif group == 2:
            address = self.base_address + OUTPUTWIDTH_2
        else:
            msg = 'group must be either 1 (channels 0-7) or 2 (channels 8-15)'
            raise ValueError(msg)

        if (width < 0) | (width > 255):
            raise ValueError('width must be between 0 and 255')

        self.vme.singleWriteD16(address, width)

    def setMajority(self, majority_level):
        if (majority_level < 1) | (majority_level > 20):
            raise ValueError('majority must be between 1 and 20')

        self.vme.singleWriteD16(self.base_address + MAJORITY,
                                majority(majority_level))

    def sendTestPulse(self):
        self.vme.singleWriteD16(self.base_address + TEST_PULSE, 1)
