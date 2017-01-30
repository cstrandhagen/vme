'''
cryoread/daq/caen2718.py
-----------------------

Created on Jun 19, 2013

@author: Christian Strandhagen (strandhagen _at_ pit.physik.uni-tuebingen.de)
'''

import numpy as np
import caenvme

from caenvme import (BoardTypes, PulserSelect, TimeUnits,
                     IOSources, OutputSelect, IOPolarity,
                     LEDPolarity, IRQLevels, VME_Error)

import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

translate_irq_levels = {'\x01': 1,
                        '\x02': 2,
                        '\x04': 3,
                        '\x08': 4,
                        '\x10': 5,
                        '\x20': 6,
                        '\x40': 7}

cvIRQ = [0x0, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40]


class v2718(object):
    '''
    Implements functionality of CAEN V2718 VME Controller Board
    using CaenVMElib.

    Only a subset of the functionality is currently implemented,
    feel free to add more. For a list of further options refer
    to the manual.
    '''
    handle = None

    def __init__(self):
        self.handle = caenvme.Init(BoardTypes.V2718)
        logger.debug('VME bridge initialised ({0})'.format(self.handle))

    def __del__(self):
        '''
        End VME connection on delete.
        '''
        if self.handle is not None:
            logger.debug('VME bridge disconnected')
            caenvme.End(self.handle)

    def singleReadD32(self, address):
        '''
        Reads a single 32-bit value from address.
        '''
        return caenvme.SingleReadD32(self.handle, address)

    def singleReadD16(self, address):
        '''
        Reads a single 16-bit value from address.
        '''
        return caenvme.SingleReadD16(self.handle, address)

    def blockReadD32(self, address, nsamples):
        '''
        Reads nsamples 32-bit values from address.
        '''
        return caenvme.BlockReadD32(self.handle, address, nsamples)

    def blockReadD16(self, address, nsamples):
        '''
        Reads nsamples 16-bit values from address.
        '''
        return caenvme.BlockReadD16(self.handle, address, nsamples)

    def singleWriteD32(self, address, data):
        '''
        Writes a single 32-bit value to address.
        '''
        caenvme.SingleWriteD32(self.handle, address, data)

    def singleWriteD16(self, address, data):
        '''
        Writes a single 16-bit value to address.
        '''
        caenvme.SingleWriteD16(self.handle, address, data)

    def configureOutput(self, output_select,
                        output_polarity, led_polarity, source):
        '''
        Configures the custom output lines on the front panel.

        You need to specify which output line to configure, its
        polarity, the corresponding LED's polarity and the internal
        source of the output.

        For details refer to the manual.
        '''
        caenvme.SetOutputConf(self.handle, output_select, output_polarity,
                              led_polarity, source)

    def enableIRQ(self, mask, enable=True):
        '''
        Enables/disables the IRQ lines specified by mask.
        '''
        if enable:
            logger.debug('enable IRQ with mask {0}'.format(mask))
            caenvme.IRQEnable(self.handle, mask)
        else:
            logger.debug('disable IRQ with mask {0}'.format(mask))
            caenvme.IRQDisable(self.handle, mask)

    def checkIRQ(self):
        '''
        Returns the active IRQ line.

        See also: waitForIRQ, IACKCycle
        '''
        logger.debug('check IRQ')
        mask = caenvme.IRQCheck(self.handle)
        print mask, int(np.log2(mask)) + 1

        return int(np.log2(mask)) + 1

    def waitForIRQ(self, mask, timeout):
        '''
        Waits for one of the IRQ lines in mask to be ative.

        Blocks until one of the valid IRQ lines are active
        or until timeout is reached.

        See also: checkIRQ, IACKCycle
        '''
        msg = 'wait for IRQ with mask {0} (timeout {1})'
        logger.debug(msg.format(mask, timeout))

        caenvme.IRQWait(self.handle, mask, timeout)

    def IACKCycle(self, irq_level):
        '''
        Performs interrupt acknowledge cycle.

        Acknowledge the interrupt on the specified line.

        See also: waitForIRQ, checkIRQ
        '''
        logger.debug('IACK cycle, IRQ level {0}'.format(irq_level))

        irq_level = cvIRQ[irq_level]
        return caenvme.IACKCycle(self.handle, irq_level)

    def startPulser(self, pulser):
        '''
        Starts one of the pulsers on the controller board.

        The pulser needs to be configured beforehand.

        See also: configurePulser, stopPulser
        '''
        logger.debug('start pulser')
        caenvme.StartPulser(self.handle, pulser)

    def stopPulser(self, pulser):
        '''
        Stops a running pulser.

        See also: startPulser, configurePulser
        '''
        logger.debug('stop pulser')
        caenvme.StopPulser(self.handle, pulser)

    def configurePulser(self, pulser, period, width, time_unit,
                        n_pulses, start_signal, reset_signal):
        '''
        Configures one of the pulsers on the controller board.

        For details refer to the manual.

        See also: startPulser, stopPulser
        '''

        caenvme.SetPulserConf(self.handle, pulser, period, width, time_unit,
                              n_pulses, start_signal, reset_signal)
