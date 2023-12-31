import gc
import time
from machine import Pin
from time import sleep, sleep_ms

TX_BASE_ADDR = 0x00
RX_BASE_ADDR = 0x00

PA_BOOST = 0x80
PA_OUTPUT_RFO_PIN = 0
PA_OUTPUT_PA_BOOST_PIN = 1

REG_FIFO = 0x00
REG_OP_MODE = 0x01
REG_FRF_MSB = 0x06
REG_FRF_MID = 0x07
REG_FRF_LSB = 0x08
REG_PA_CONFIG = 0x09
REG_OCP = 0x0b
REG_LNA = 0x0c
REG_FIFO_ADDR_PTR = 0x0d
REG_FIFO_TX_BASE_ADDR = 0x0e
REG_FIFO_RX_BASE_ADDR = 0x0f
REG_FIFO_RX_CURRENT_ADDR = 0x10
REG_IRQ_FLAGS = 0x12
REG_RX_NB_BYTES = 0x13
REG_PKT_RSSI_VALUE = 0x1a
REG_PKT_SNR_VALUE = 0x1b
REG_MODEM_CONFIG_1 = 0x1d
REG_MODEM_CONFIG_2 = 0x1e
REG_PREAMBLE_MSB = 0x20
REG_PREAMBLE_LSB = 0x21
REG_PAYLOAD_LENGTH = 0x22
REG_MODEM_CONFIG_3 = 0x26
REG_MODEM_PPM_COR = 0x27
REG_MODEM_FEI_MSB = 0x28
REG_MODEM_FEI_MID = 0x29
REG_MODEM_FEI_LSB = 0x2A
REG_DETECTION_OPTIMIZE = 0x31
REG_DETECTION_THRESHOLD = 0x37
REG_SYNC_WORD = 0x39
REG_IMAGE_CAL = 0x3B
REG_TEMP = 0x3C
REG_DIO_MAPPING_1 = 0x40
REG_VERSION = 0x42
REG_PA_DAC = 0x4D

MODE_LORA = 0x80
MODE_SLEEP = 0x00
MODE_STDBY = 0x01
MODE_TX = 0x03
MODE_RX_CONTINUOUS = 0x05

IRQ_TX_DONE_MASK = 0x08
IRQ_PAYLOAD_CRC_ERROR_MASK = 0x20

MAX_PKT_LENGTH = 255

RFLR_OPMODE_LONGRANGEMODE = 0x80

REG_PA_DAC_20DBM = 0x87

class LoRa:
    cntRxFrame = 0
    cntTxFrame = 0
    cntFrmTout = 0
    crcFrameRxCntOk = 0
    crcFrameRxCntErr = 0
    def __init__(self, spi, **kw):
        self.spi = spi
        self.cs = kw['cs']
        self.rx = kw['rx']
        while self._read(REG_VERSION) != 0x12:
            time.sleep_ms(100)            
            #raise Exception('Invalid version or bad SPI connection')
            print("Invalid version or bad SPI connection")
            print("Wersja:" + str(self._read(REG_VERSION)))
        self.sleep()
        self.set_frequency(kw.get('frequency', 433.0))
        self.set_bandwidth(kw.get('bandwidth', 250000))
        self.set_coding_rate(kw.get('coding_rate', 5))
        self.set_preamble_length(kw.get('preamble_length', 64))
        self.set_crc(kw.get('crc', True))
        # set LNA boost
#        self._write(REG_LNA, self._read(REG_LNA) | 0x03)   # rsv Gain, Boost on 150% normy
#        self._write(REG_LNA, self._read(REG_LNA) | 0xC0)   # min Gain, Boost off
#        self._write(REG_LNA, self._read(REG_LNA) | 0x20)   # max Gain, Boost off
        self._write(REG_LNA, self._read(REG_LNA) | 0x23)   # max Gain, Boost on 150% normy
#        self._write(REG_LNA, self._read(REG_LNA) | 0x00)   # rsv Gain, Boost off
        # set auto AGC
#        self._write(REG_MODEM_CONFIG_3, 0x00)  # Gain by register REG_LNA
        self._write(REG_MODEM_CONFIG_3, 0x04)  # Gain by AGC
        self.set_spreading_factor(kw.get('spreading_factor', 12))
        self.set_tx_power(kw.get('tx_power', 24))
        if self._sf == 6:
            implicit = True
        else:   
            implicit = kw.get('implicit', False)
        self._implicit = not(implicit)
        self.set_implicit(implicit)
        self.set_sync_word(kw.get('sync_word', 0x75))
        self._on_recv = kw.get('on_recv', None)
        self.set_ppm_correction(kw.get('ppm_cor', 0x00))
        self._write(REG_OCP, 27)  # Zgodnie z datashit zabezpieczenie nadpradowe na max 240mA     
        self._write(REG_PA_DAC, REG_PA_DAC_20DBM)  # Zgodnie z datashit tak ma byc dla 20dBm
        self._write(REG_FIFO_TX_BASE_ADDR, TX_BASE_ADDR)
        self._write(REG_FIFO_RX_BASE_ADDR, RX_BASE_ADDR)
        self.standby()
#        print(self._read(REG_MODEM_CONFIG_1))
#        print(self._read(REG_MODEM_CONFIG_2))
#        print(self._read(REG_MODEM_CONFIG_3))
#        print(self._read(REG_DETECTION_OPTIMIZE))
#        print(self._read(REG_DETECTION_THRESHOLD))
#        print(self._read(REG_PA_CONFIG))
#        print(self._read(REG_LNA))
#        print(self._read(REG_PA_DAC))
        

    def begin_packet(self):
        self.standby()
        self._write(REG_FIFO_ADDR_PTR, TX_BASE_ADDR)
        self._write(REG_PAYLOAD_LENGTH, 0)

    def end_packet(self):
        self._write(REG_OP_MODE, MODE_LORA | MODE_TX)
        while (self._read(REG_IRQ_FLAGS) & IRQ_TX_DONE_MASK) == 0:
            pass
        self._write(REG_IRQ_FLAGS, IRQ_TX_DONE_MASK)
        gc.collect()

    def write_packet(self, b):
        n = self._read(REG_PAYLOAD_LENGTH)
        m = len(b)
        p = MAX_PKT_LENGTH - TX_BASE_ADDR
        if n + m > p:
            raise ValueError('Max payload length is ' + str(p))
        for i in range(m):
            self._write(REG_FIFO, b[i])
        self._write(REG_PAYLOAD_LENGTH, n + m)

    def send(self, x):
        if isinstance(x, str):
            x = x.encode()
        self.begin_packet()
        self.write_packet(x)
        self.end_packet()

    def _get_irq_flags(self):
        f = self._read(REG_IRQ_FLAGS)
        self._write(REG_IRQ_FLAGS, f)
        return f

    def get_rssi(self):
        rssi = self._read(REG_PKT_RSSI_VALUE)
        if self._frequency >= 779.0:
            return rssi - 157
        return rssi - 164

    def get_snr(self):
        return self._read(REG_PKT_SNR_VALUE) * 0.25

    def get_temperature(self):
        previousOpMode = self._read(REG_OP_MODE)
        if ((previousOpMode & RFLR_OPMODE_LONGRANGEMODE) == RFLR_OPMODE_LONGRANGEMODE):
            self._write(REG_OP_MODE, RFLR_OPMODE_LONGRANGEMODE | MODE_SLEEP)   
        self._write(REG_OP_MODE, MODE_SLEEP)
        self._write(REG_OP_MODE, 0x04)
        imageCal = self._read(REG_IMAGE_CAL) & 0xFE
        self._write(REG_IMAGE_CAL, imageCal)
        time.sleep_us(150)
        imageCal = self._read(REG_IMAGE_CAL) | 0x01
        self._write(REG_IMAGE_CAL, imageCal)
        self._write(REG_OP_MODE, MODE_SLEEP)        
        temperatura = self._read(REG_TEMP)
        if ((temperatura & 0x80) == 0x80):
            temperatura = 255 - temperatura
        else:
            temperatura = -temperatura 
        if ((previousOpMode & RFLR_OPMODE_LONGRANGEMODE) == RFLR_OPMODE_LONGRANGEMODE):
            self._write(REG_OP_MODE, RFLR_OPMODE_LONGRANGEMODE | MODE_SLEEP)   
        self._write(REG_OP_MODE, previousOpMode)
        return (temperatura + 10)

    def get_efi(self):
        msb = self._read(REG_MODEM_FEI_MSB)
        mid = self._read(REG_MODEM_FEI_MID)
        lsb = self._read(REG_MODEM_FEI_LSB)        
        efi = ((msb<<16)|(mid<<8)|lsb)
        if (efi & 0x80000):
            efi = (efi & 0x7FFFF) - 0x80000
        return (efi)

    def standby(self):
        self._write(REG_OP_MODE, MODE_LORA | MODE_STDBY)

    def sleep(self):
        self._write(REG_OP_MODE, MODE_LORA | MODE_SLEEP)

    def set_tx_power(self, level, outputPin=PA_OUTPUT_PA_BOOST_PIN):
        if outputPin == PA_OUTPUT_RFO_PIN:
            level = min(max(level, 0), 14)
            self._write(REG_PA_CONFIG, 0x70 | level)
        else:
            level = min(max(level, 2), 17)
            self._write(REG_PA_CONFIG, PA_BOOST | (level - 2))

    def set_frequency(self, frequency):
        self._frequency = frequency
        hz = frequency * 1000000.0
        x = round(hz / 61.03515625)
        self._write(REG_FRF_MSB, (x >> 16) & 0xff)
        self._write(REG_FRF_MID, (x >> 8) & 0xff)
        self._write(REG_FRF_LSB, x & 0xff)

    def set_ppm_correction(self, ppm_cor):
        self._ppm_cor = ppm_cor
        self._write(REG_MODEM_PPM_COR, ppm_cor)

    def set_spreading_factor(self, sf):
        self._sf = sf        
        if sf < 6 or sf > 12:
            raise ValueError('Spreading factor must be between 6-12')
        self._write(REG_DETECTION_OPTIMIZE, 0xc5 if sf == 6 else 0xc3)
        self._write(REG_DETECTION_THRESHOLD, 0x0c if sf == 6 else 0x0a)
        reg2 = self._read(REG_MODEM_CONFIG_2)
        self._write(REG_MODEM_CONFIG_2, (reg2 & 0x0f) | ((sf << 4) & 0xf0))
        reg3 = self._read(REG_MODEM_CONFIG_3)
        self._write(REG_MODEM_CONFIG_3, (reg3 |0x08) if (sf>10 and self._bandwidth<250000) else (reg3 & 0xF7))

    def set_bandwidth(self, bw):
        self._bandwidth = bw
        bws = (7800, 10400, 15600, 20800, 31250, 41700, 62500, 125000, 250000)
        i = 9
        for j in range(len(bws)):
            if bw <= bws[j]:
                i = j
                break
        x = self._read(REG_MODEM_CONFIG_1) & 0x0f
        self._write(REG_MODEM_CONFIG_1, x | (i << 4))

    def set_coding_rate(self, denom):
        denom = min(max(denom, 5), 8)
        self._cr = denom
        cr = denom - 4
        reg1 = self._read(REG_MODEM_CONFIG_1)
        self._write(REG_MODEM_CONFIG_1, (reg1 & 0xf1) | (cr << 1))

    def set_preamble_length(self, n):
        self._pl = n
        self._write(REG_PREAMBLE_MSB, (n >> 8) & 0xff)
        self._write(REG_PREAMBLE_LSB, (n >> 0) & 0xff)

    def set_crc(self, crc=False):
        modem_config_2 = self._read(REG_MODEM_CONFIG_2)
        if crc:
            config = modem_config_2 | 0x04
        else:
            config = modem_config_2 & 0xfb
        self._write(REG_MODEM_CONFIG_2, config)

    def set_sync_word(self, sw):
        self._sw = sw
        self._write(REG_SYNC_WORD, sw) 

    def freq_sync_rx(self):
        efi = self.get_efi()
        ferror = ((efi*16777216)/32000000)*((self._bandwidth/1000)/500)
        new_freq = (1000000*self._frequency - ferror)/1000000
        return new_freq
    
    def set_implicit(self, implicit=False):
        if self._implicit != implicit:
            self._implicit = implicit
            modem_config_1 = self._read(REG_MODEM_CONFIG_1)
            if implicit:
                config = modem_config_1 | 0x01
            else:
                config = modem_config_1 & 0xfe
            self._write(REG_MODEM_CONFIG_1, config)

    def on_recv(self, callback):
        self._on_recv = callback
        if self.rx:
            if callback:
                self._write(REG_DIO_MAPPING_1, 0x00)
                self.rx.irq(handler=self._irq_recv, trigger=Pin.IRQ_RISING)
            else:
                self.rx.irq(handler=None, trigger=0)

    def recv(self):
        self._write(REG_OP_MODE, MODE_LORA | MODE_RX_CONTINUOUS) 

    def _irq_recv(self, event_source):
        f = self._get_irq_flags()
        if f & IRQ_PAYLOAD_CRC_ERROR_MASK == 0:
            if self._on_recv:
                self._on_recv(self._read_payload())

    def _read_payload(self):
        self._write(REG_FIFO_ADDR_PTR, self._read(REG_FIFO_RX_CURRENT_ADDR))
        if self._implicit:
            n = self._read(REG_PAYLOAD_LENGTH)
        else:
            n = self._read(REG_RX_NB_BYTES)
        payload = bytearray()
        for i in range(n):
            payload.append(self._read(REG_FIFO))
        gc.collect()
        return bytes(payload)

    def _transfer(self, addr, x=0x00):
        resp = bytearray(1)
        self.cs.value(0)
        self.spi.write(bytes([addr]))
        self.spi.write_readinto(bytes([x]), resp)
        self.cs.value(1)
        return resp

    def _read(self, addr):
        x = self._transfer(addr & 0x7f) 
        return int.from_bytes(x, 'big')

    def _write(self, addr, x):
        self._transfer(addr | 0x80, x)

    def clrStat(self):
        cntRxFrame = 0
        cntTxFrame = 0
        cntFrmTout = 0
        crcFrameRxCntOk = 0
        crcFrameRxCntErr = 0
