'''
cryoread/daq/sis3302.py
-----------------------

Created on Jun 19, 2013

@author: Christian Strandhagen (strandhagen _at_ pit.physik.uni-tuebingen.de)
'''

import numpy as np

import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# CONSTANTS

MAX_NOF_SAMPLES = 0x2000000      # = 32MSample DO NOT CHANGE!
MAX_SAMPLES_PER_PAGE = 0x400000  # = 4 MSample DO NOT CHANGE!

# ADDRESSES

CONTROL_STATUS = 0x0
MODID = 0x4
IRQ_CONFIG = 0x8
IRQ_CONTROL = 0xC
ACQUISITION_CONTROL = 0x10
START_DELAY = 0x14
STOP_DELAY = 0x18
MAX_NOF_EVENT = 0x20
ACTUAL_EVENT_COUNTER = 0x24
ADC_MEMORY_PAGE = 0x34
DAC_CONTROL_STATUS = 0x50
DAC_DATA = 0x54

# KEY ADRESSES

KEY_RESET = 0x400
KEY_ARM = 0x410
KEY_DISARM = 0x414
KEY_START = 0x418
KEY_STOP = 0x41C
KEY_RESET_DDR2_LOGIC = 0x428
KEY_TIMESTAMP_CLR = 0x42C

# READ ONLY REGISTERS

TIMESTAMP_DIRECTORY = 0x10000

# ALL ADC STUFF

EVENT_CONFIG = [0x01000000,
                0x02000000,
                0x02000000,
                0x02800000,
                0x02800000,
                0x03000000,
                0x03000000,
                0x03800000,
                0x03800000]

EVENT_DIRECTORY = [0x02010000,
                   0x02018000,
                   0x02810000,
                   0x02818000,
                   0x03010000,
                   0x03018000,
                   0x03810000,
                   0x03818000]

ADC_INPUT_MODE = [0x0100000C,
                  0x0200000C,
                  0x0200000C,
                  0x0280000C,
                  0x0280000C,
                  0x03000020,
                  0x03000020,
                  0x03800020,
                  0x03800020]

ADC_OFFSET = [None,
              0x04000000,
              0x04800000,
              0x05000000,
              0x05800000,
              0x06000000,
              0x06800000,
              0x07000000,
              0x07800000]

EVENT_CONFIG_ALL_ADC = 0x01000000
SAMPLE_LENGTH_ALL_ADC = 0x01000004
SAMPLE_START_ADDRESS_ALL_ADC = 0x01000008
ADC_INPUT_MODE_ALL_ADC = 0x0100000C
TRIGGER_FLAG_CLR_CNT_ALL_ADC = 0x0100002C

# ADC 1/2

ADC_INPUT_MODE_ADC12 = 0x0200000C
ACTUAL_SAMPLE_VALUE_ADC12 = 0x02000020
DDR2_TEST_REGISTER_ADC12 = 0x02000028
TRIGGER_FLAG_CLR_CNT_ADC12 = 0x0200002C

# ADC 1

ACTUAL_SAMPLE_ADDRESS_ADC1 = 0x02000010
TRIGGER_SETUP_ADC1 = 0x02000030
TRIGGER_THRESHOLD_ADC1 = 0x02000034
EVENT_DIRECTORY_ADC1 = 0x02010000

# ADC 2
ACTUAL_SAMPLE_ADDRESS_ADC2 = 0x02000014
TRIGGER_SETUP_ADC2 = 0x02000038
TRIGGER_THRESHOLD_ADC2 = 0x0200003C
EVENT_DIRECTORY_ADC2 = 0x02018000

# TODO: implement other adcs

# ACQUISITION CONTROL

ACQ_SET_CLOCK_TO_100MHZ = 0x70000000
ACQ_SET_CLOCK_TO_50MHZ = 0x60001000
ACQ_SET_CLOCK_TO_25MHZ = 0x50002000
ACQ_SET_CLOCK_TO_10MHZ = 0x40003000
ACQ_SET_CLOCK_TO_1MHZ = 0x30004000
ACQ_SET_CLOCK_TO_LEMO_RANDOM_CLOCK_IN = 0x20005000
ACQ_SET_CLOCK_TO_LEMO_CLOCK_IN = 0x10006000
ACQ_SET_CLOCK_TO_P2_CLOCK_IN = 0x00007000

ACQ_DISABLE_LEMO_START_STOP = 0x01000000
ACQ_ENABLE_LEMO_START_STOP = 0x00000100

ACQ_DISABLE_LEMO1_TIMESTAMP_CLR = 0x02000000
ACQ_ENABLE_LEMO1_TIMESTAMP_CLR = 0x00000200

ACQ_DISABLE_INTERNAL_TRIGGER = 0x00400000
ACQ_ENABLE_INTERNAL_TRIGGER = 0x00000040

ACQ_DISABLE_MULTIEVENT = 0x00200000
ACQ_ENABLE_MULTIEVENT = 0x00000020

ACQ_DISABLE_AUTOSTART = 0x00100000
ACQ_ENABLE_AUTOSTART = 0x00000010

# EVENT_CONFIG

EVENT_CONF_ENABLE_SAMPLE_LENGTH_STOP = 0x20
EVENT_CONF_ENABLE_WRAP_PAGE_MODE = 0x10

EVENT_CONF_PAGE_SIZE_16M_WRAP = 0x0
EVENT_CONF_PAGE_SIZE_4M_WRAP = 0x1
EVENT_CONF_PAGE_SIZE_1M_WRAP = 0x2
EVENT_CONF_PAGE_SIZE_256K_WRAP = 0x3

EVENT_CONF_PAGE_SIZE_64K_WRAP = 0x4
EVENT_CONF_PAGE_SIZE_16K_WRAP = 0x5
EVENT_CONF_PAGE_SIZE_4K_WRAP = 0x6
EVENT_CONF_PAGE_SIZE_1K_WRAP = 0x7

EVENT_CONF_PAGE_SIZE_512_WRAP = 0x8
EVENT_CONF_PAGE_SIZE_256_WRAP = 0x9
EVENT_CONF_PAGE_SIZE_128_WRAP = 0xA
EVENT_CONF_PAGE_SIZE_64_WRAP = 0xB

# IRQ_CONFIG

IRQ_ENABLE = 0x800
IRQ_SOURCE_ENABLE = [0x1, 0x2]
IRQ_SOURCE_DISABLE = [0x10000, 0x20000]

# PAGE_SIZE 'enum'
SIS_PAGE_SIZE = {64: 0xB,
                 128: 0xA,
                 256: 0x9,
                 512: 0x8,
                 1024: 0x7,
                 4096: 0x6,
                 16384: 0x5,
                 65536: 0x4,
                 262144: 0x3,
                 1048576: 0x2,
                 4194304: 0x1,
                 16777216: 0x0}

CLK_SRC = {'100MHz': 0x70000000,
           '50MHz': 0x60001000,
           '25MHz': 0x50002000,
           '10MHz': 0x40003000,
           '1MHz': 0x30004000,
           'random': 0x20005000,
           'external': 0x10006000,
           'p2': 0x00007000}


def decode_module_id(modid):
    '''
    Decodes Module ID sent by SIS FADC.

    Returns a string containing model number, and firmware revision.
    '''
    msg = ''

    for i in xrange(32, 0, -4):
        n = (modid & (2**i - 1)) >> (i - 4)
        msg += str(n)

    msg = 'SIS %s (FW %s)' % (msg[:4], '.'.join(msg[4:]))

    return msg


class SIS3302(object):
    '''
    Implements the functionality of the SIS3302 FADC.
    '''
    def __init__(self, vme, base_address):
        self.vme = vme
        self.base_address = base_address
        self.reset()

    def getModuleID(self):
        '''
        Reads module ID and firmware revision.
        '''
        logger.debug('get module ID')
        modid = self.vme.singleReadD32(self.base_address + MODID)

        return decode_module_id(modid)

    def reset(self):
        '''
        Resets all settings to factory defaults.
        '''
        logger.debug('reset')
        self.vme.singleWriteD32(self.base_address + KEY_RESET, 1)

    def clearTimestamps(self):
        logger.debug('clear timestamps')
        self.vme.singleWriteD32(self.base_address + KEY_TIMESTAMP_CLR, 1)

    def enableAutostart(self, enable=True):
        if enable:
            logger.debug('enable autostart')
            data = ACQ_ENABLE_AUTOSTART
        else:
            logger.debug('disable autostart')
            data = ACQ_DISABLE_AUTOSTART

        self.vme.singleWriteD32(self.base_address + ACQUISITION_CONTROL, data)

    def enableMultiEvent(self, enable=True):
        if enable:
            logger.debug('enable multi-event mode')
            data = ACQ_ENABLE_MULTIEVENT
        else:
            logger.debug('disable multi-event mode')
            data = ACQ_DISABLE_MULTIEVENT

        self.vme.singleWriteD32(self.base_address + ACQUISITION_CONTROL, data)

    def enableInternalTrigger(self, enable=True):
        if enable:
            logger.debug('enable internal trigger')
            data = ACQ_ENABLE_INTERNAL_TRIGGER
        else:
            logger.debug('disable internal trigger')
            data = ACQ_DISABLE_INTERNAL_TRIGGER

        self.vme.singleWriteD32(self.base_address + ACQUISITION_CONTROL, data)

    def enableFrontPanelStartStop(self, enable=True):
        if enable:
            logger.debug('enable front panel start/stop')
            data = ACQ_ENABLE_LEMO_START_STOP
        else:
            logger.debug('disable front panel start/stop')
            data = ACQ_DISABLE_LEMO_START_STOP

        self.vme.singleWriteD32(self.base_address + ACQUISITION_CONTROL, data)

    def readAcquisitionControl(self):
        logger.debug('read acquisition control')
        return self.vme.singleReadD32(self.base_address + ACQUISITION_CONTROL)

    def setStartDelay(self, start_delay):
        logger.debug('set start delay to {0}'.format(start_delay))
        self.vme.singleWriteD32(self.base_address + START_DELAY, start_delay)

    def getStartDelay(self):
        logger.debug('get start delay')
        return self.vme.singleReadD32(self.base_address + START_DELAY)

    def getStopDelay(self):
        logger.debug('get stop delay')
        return self.vme.singleReadD32(self.base_address + STOP_DELAY)

    def setStopDelay(self, stop_delay):
        logger.debug('set stop delay to {0}'.format(stop_delay))
        self.vme.singleWriteD32(self.base_address + STOP_DELAY, stop_delay)

    def setMaxNoOfEvents(self, max_n):
        logger.debug('set max number of events to {0}'.format(max_n))
        self.vme.singleWriteD32(self.base_address + MAX_NOF_EVENT, max_n)

    def getMaxNoOfEvents(self):
        logger.debug('get max number of events')
        return self.vme.singleReadD32(self.base_address + MAX_NOF_EVENT)

    def enablePageWrap(self, enable=True):
        data = self.readEventConfiguration(1)

        data |= EVENT_CONF_ENABLE_WRAP_PAGE_MODE

        if not enable:
            logger.debug('disable page wrap')
            data ^= EVENT_CONF_ENABLE_WRAP_PAGE_MODE
        else:
            logger.debug('enable page wrap')

        self.vme.singleWriteD32(self.base_address + EVENT_CONFIG_ALL_ADC, data)

    def readEventConfiguration(self, adc=1):
        if adc < 1 or adc > 8:
            raise IndexError('ADC number must be between 1 and 8')

        logger.debug('read event config for adc {0}'.format(adc))

        return self.vme.singleReadD32(self.base_address + EVENT_CONFIG[adc])

    def setPageSize(self, page_size):
        page_size = SIS_PAGE_SIZE[page_size]

        data = self.readEventConfiguration(1)
        data &= 0xfffffff0
        data |= page_size

        logger.debug('set page size to {0} ({1})'.format(page_size, data))

        self.vme.singleWriteD32(self.base_address + EVENT_CONFIG[0], data)

    def readIRQConfiguration(self):
        logger.debug('read IRQ config')
        return self.vme.singleReadD32(self.base_address + IRQ_CONFIG)

    def enableIRQ(self, enable=True):
        data = self.readIRQConfiguration()
        data |= IRQ_ENABLE

        if not enable:
            logger.debug('disable IRQ')
            data ^= IRQ_ENABLE
        else:
            logger.debug('enable IRQ')

        self.vme.singleWriteD32(self.base_address + IRQ_CONFIG, data)

    def setIRQVector(self, vector):
        if vector < 0:
            raise ValueError('vector has to be positive')

        if vector > 255:
            raise ValueError('vector must be <= 255')

        data = self.readIRQConfiguration()
        data &= 0xffffff00
        data |= vector

        logger.debug('set IRQ vector to {0} ({1})'.format(vector, data))

        self.vme.singleWriteD32(self.base_address + IRQ_CONFIG, data)

    def setIRQLevel(self, irq_level):
        if irq_level < 0:
            raise ValueError('irq_level must be positive')

        if irq_level > 7:
            raise ValueError('irq_level must be <= 7')

        data = self.readIRQConfiguration()
        data &= 0xfffff8ff
        data |= irq_level << 8

        logger.debug('set IRQ level to {0} ({1})'.format(irq_level, data))

        self.vme.singleWriteD32(self.base_address + IRQ_CONFIG, data)

    def getIRQLevel(self):
        logger.debug('get IRQ level')
        data = self.readIRQConfiguration()

        return data & 0x700

    def getIRQVector(self):
        logger.debug('get IRQ vector')
        data = self.readIRQConfiguration()

        return data & 0xff

    def IRQEnabled(self):
        logger.debug('IRQ enabled?')
        data = self.readIRQConfiguration()

        return bool(data & IRQ_ENABLE)

    def enableIRQSource(self, src, enable=True):
        if src < 0 or src > 1:
            raise ValueError('irq source must be either 1 or 2')

        if enable:
            logger.debug('enable IRQ source {0}'.format(src))
            data = IRQ_SOURCE_ENABLE[src]
        else:
            logger.debug('disable IRQ source {0}'.format(src))
            data = IRQ_SOURCE_DISABLE[src]

        self.vme.singleWriteD32(self.base_address + IRQ_CONTROL, data)

    def readIRQControl(self):
        logger.debug('read IRQ control')
        return self.vme.singleReadD32(self.base_address + IRQ_CONTROL)

    def IRQSourceEnabled(self, src):
        logger.debug('IRQ source {0} enabled?'.format(src))
        if src < 0 or src > 1:
            raise ValueError('irq source must be either 1 or 2')

        data = self.readIRQControl()

        return bool(data & IRQ_SOURCE_ENABLE[src])

    def armSamplingLogic(self):
        logger.debug('arm sampling logic')
        self.vme.singleWriteD32(self.base_address + KEY_ARM, 1)

    def disarmSamplingLogic(self):
        logger.debug('disarm sampling logic')
        self.vme.singleWriteD32(self.base_address + KEY_DISARM, 1)

    def startSampling(self):
        logger.debug('start sampling')
        self.vme.singleWriteD32(self.base_address + KEY_START, 1)

    def stopSampling(self):
        logger.debug('stop sampling')
        self.vme.singleWriteD32(self.base_address + KEY_STOP, 1)

    def readEventDirectory(self, adc=1, n=512):
        if adc < 1 or adc > 8:
            raise IndexError('adc number must be between 1 and 8')

        address = self.base_address + EVENT_DIRECTORY[adc - 1]

        msg = 'read {0} samples from event directory of adc {1}'
        logger.debug(msg.format(n, adc))

        return self.vme.blockReadD32(address, n)

    def readTimestampDirectory(self, n=512):
        logger.debug('read {0} timestamps'.format(n))

        address = self.base_address + TIMESTAMP_DIRECTORY
        ts = self.vme.blockReadD32(address, 2 * n)

        # ts = np.array([(high<<32)+low for high,low in zip(ts[::2],ts[1::2])])

        high = ts[::2]
        low = ts[1::2]

        return high * 2**32 + low

    def readADCInputModeRegister(self, adc):
        if adc < 1 or adc > 8:
            raise IndexError('adc number must be between 1 and 8')

        logger.debug('read input mode register of adc {0}'.format(adc))

        return self.vme.singleReadD32(self.base_address + ADC_INPUT_MODE[adc])

    def setADCTestStartData(self, start_data):
        data = self.readADCInputModeRegister(1)
        data &= 0xffff0000
        data |= (start_data & 0xfffd)

        msg = 'set adc test start data to {0} ({1})'
        logger.debug(msg.format(start_data, data))

        address = self.base_address + ADC_INPUT_MODE[0]
        self.vme.singleWriteD32(address, data)

    def getADCTestStartData(self, adc=1):
        logger.debug('get test start data of adc {0}'.format(adc))
        data = self.readADCInputModeRegister(adc)

        return data & 0xffff

    def enableADCTestDataMode(self, enable=True):
        data = self.readADCInputModeRegister(1)
        data |= 0x10000

        if not enable:
            logger.debug('disable adc test data mode')
            data ^= 0x10000
        else:
            logger.debug('enable adc test data mode')

        address = self.base_address + ADC_INPUT_MODE[0]
        self.vme.singleWriteD32(address, data)

    def readData(self, adc, page_size, n_events):
        msg = 'read {0} events from adc {1} with page size {2}'
        logger.debug(msg.format(n_events, adc, page_size))

        samples_per_page = 0x400000

        address = self.base_address + ADC_OFFSET[adc]
        n_samples = page_size * n_events

        # check if more than 4MSamples are requested at once
        if n_samples > samples_per_page:
            n_pages = n_samples / samples_per_page
            logger.debug('splitting into {0} pages'.format(n_pages))

            samples = [samples_per_page for i in xrange(n_pages)]
            rest = n_samples - (n_pages * samples_per_page)

            if rest > 0:
                samples.append(rest)

            data = np.array([], dtype='uint16')

            for i, n in enumerate(samples):
                self.selectMemoryPage(i)
                readout = self.vme.blockReadD16(address, n)
                data = np.concatenate([data, readout])
        else:
            data = self.vme.blockReadD16(address, n_samples)

        return data.reshape(n_events, page_size)

    def selectMemoryPage(self, page):
        logger.debug('select memory page {0}'.format(page))
        if page < 0 or page > 7:
            raise IndexError('page must be between 0 and 7')

        address = self.base_address + ADC_MEMORY_PAGE
        self.vme.singleWriteD32(address, page)

    def setClockSource(self, clk):
        data = CLK_SRC[clk]

        logger.debug('set clock source to {0} ({1})'.format(clk, data))

        self.vme.singleWriteD32(self.base_address + ACQUISITION_CONTROL, data)
