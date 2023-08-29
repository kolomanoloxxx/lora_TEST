from lora import LoRa
from ST7735 import TFT,TFTColor
from sysfont import sysfont
from machine import SPI,Pin
from machine import Pin, Timer, PWM, RTC
from crc import Crc
import time
import math
import gc
import random
import os

# definicje stalych znakowych uzywanych wielokrotnie
TEST_VER_STR = "Test LoRa ver.:1.04"
MASTER_STR = "LoRa Master"
SLAVE_STR = "LoRa Slave"
LOG_SIZE_KB = 128

# definicje czasow opoznienia oczekiwania na ramke
# wartosc razy 10ms daje okres czasu 
TIME_OUT_500000_12_8 = 150   # 1500 msec -- ok
TIME_OUT_250000_12_8 = 300   # 3000 msec -- ok
TIME_OUT_125000_12_8 = 600   # 6000 msec -- ok
TIME_OUT_62500_12_8  = 1200  # 12000 msec -- ok
TIME_OUT_41700_12_8  = 1800  # 18000 msec -- ok
TIME_OUT_31250_12_8  = 2400  # 34000 msec -- ok
TIME_OUT_20800_12_8  = 3600  # 36000 msec -- slabo
TIME_OUT_15600_12_8  = 4800  # 48000 msec -- bardzo slabo
TIME_OUT_10400_12_8  = 7200  # 72000 msec -- nie dziala
TIME_OUT_7800_12_8   = 9600  # 96000 msec -- nie dziala

TIME_OUT_7800_7_5    = 300   # 3000 msec -- ok
TIME_OUT_7800_7_8    = 300   # 3000 msec -- ok
TIME_OUT_7800_8_8    = 600   # 6000 msec -- ok
TIME_OUT_7800_9_8    = 1200  # 12000 msec -- slabo
TIME_OUT_7800_10_8   = 2400  # 24000 msec -- bardzo slabo
TIME_OUT_7800_11_8   = 4800  # 48000 msec -- nie dziala

# parametry dla LORA Ra-02:
# zakrse czestotliwosci: 410..525MHz
# max transmit power 18dBm +-1dBm
# dla SF = 12 czulosc odbiornika -141dBm, SNR = -20dB
# dla SF = 10 czulosc odbiornika -134..135dBm, SNR = -15dB
# dla SF = 7 czulosc odbiornika -125..126dBm, SNR = -7dB

LoRaMaster = 1

cntRxFrame = 0
cntTxFrame = 0
cntFrmTout = 0
crcFrameRxCntOk = 0
crcFrameRxCntErr = 0
lineLCD = 0
respFlag = 0
logNr = 0

dataFrameRx = bytearray(16)
# reset do lora RA02 na SX1278
# dokumentacja SX1278 mowi ze stanem aktywnym jest stan niski dla wejscia resetu
# minimalny czas stanu aktywnego to 100us dajemy z zapasem 200us
# minimalny czas po zmianie ze stanu aktywnego na nieaktywny na resecie to 5ms dajemy z zapasem 10ms
loraResetPin = Pin(7, Pin.OUT)
led = Pin(25, Pin.OUT)

# podswietlenie LCD z PWM na 90%
podswietlenie = 90
bl = PWM(Pin(13))
bl.freq(1000)
bl.duty_u16(int((podswietlenie/100)*65535))

timer = Timer()

spi = SPI(1, baudrate=80000000, polarity=0, phase=0, sck=Pin(10), mosi=Pin(11), miso=None)
tft=TFT(spi,16,17,18)
tft.initr()
tft.rgb(True)

rtc = machine.RTC()
rtc.datetime((2023, 8, 29, 0, 00, 00, 0, 0))

# tododu srududu do zrobienia ustawianie daty i czasu

loraResetPin.low()
time.sleep_us(200)
loraResetPin.high()
time.sleep_ms(10)

try:
	spi_lora = SPI(
                        0,
                        baudrate=10000000,
                        polarity=0,
                        phase=0,
                        sck=Pin(2, Pin.OUT, Pin.PULL_DOWN),
                        mosi=Pin(3, Pin.OUT, Pin.PULL_UP),
                        miso=Pin(4, Pin.IN, Pin.PULL_UP),
                  )
	spi_lora.init()

except Exception as e:
	print(e)
	if spi_lora:
		spi_lora.deinit()
		spi_LORA = None

# Setup LoRa
lora = LoRa(
                spi_lora,
                cs=Pin(5, Pin.OUT),
                rx=Pin(6, Pin.IN), #receiver IRQ
                frequency=433,
                bandwidth=7800,
                spreading_factor=8,
                coding_rate=8,
            )

# Receive handler
def handler(dataRx):
    global respFlag, dataFrameRx
    dataFrameRx = dataRx
    respFlag = 1

def blink(timer):
    led.toggle()
    
def testlines(color):
    tft.fill(TFT.BLACK)
    for x in range(0, tft.size()[0], 6):
        tft.line((0,0),(x, tft.size()[1] - 1), color)
    for y in range(0, tft.size()[1], 6):
        tft.line((0,0),(tft.size()[0] - 1, y), color)

    tft.fill(TFT.BLACK)
    for x in range(0, tft.size()[0], 6):
        tft.line((tft.size()[0] - 1, 0), (x, tft.size()[1] - 1), color)
    for y in range(0, tft.size()[1], 6):
        tft.line((tft.size()[0] - 1, 0), (0, y), color)

    tft.fill(TFT.BLACK)
    for x in range(0, tft.size()[0], 6):
        tft.line((0, tft.size()[1] - 1), (x, 0), color)
    for y in range(0, tft.size()[1], 6):
        tft.line((0, tft.size()[1] - 1), (tft.size()[0] - 1,y), color)

    tft.fill(TFT.BLACK)
    for x in range(0, tft.size()[0], 6):
        tft.line((tft.size()[0] - 1, tft.size()[1] - 1), (x, 0), color)
    for y in range(0, tft.size()[1], 6):
        tft.line((tft.size()[0] - 1, tft.size()[1] - 1), (0, y), color)

def testfastlines(color1, color2):
    tft.fill(TFT.BLACK)
    for y in range(0, tft.size()[1], 5):
        tft.hline((0,y), tft.size()[0], color1)
    for x in range(0, tft.size()[0], 5):
        tft.vline((x,0), tft.size()[1], color2)

def testdrawrects(color):
    tft.fill(TFT.BLACK);
    for x in range(0,tft.size()[0],6):
        tft.rect((tft.size()[0]//2 - x//2, tft.size()[1]//2 - x/2), (x, x), color)

def testfillrects(color1, color2):
    tft.fill(TFT.BLACK);
    for x in range(tft.size()[0],0,-6):
        tft.fillrect((tft.size()[0]//2 - x//2, tft.size()[1]//2 - x/2), (x, x), color1)
        tft.rect((tft.size()[0]//2 - x//2, tft.size()[1]//2 - x/2), (x, x), color2)


def testfillcircles(radius, color):
    for x in range(radius, tft.size()[0], radius * 2):
        for y in range(radius, tft.size()[1], radius * 2):
            tft.fillcircle((x, y), radius, color)

def testdrawcircles(radius, color):
    for x in range(0, tft.size()[0] + radius, radius * 2):
        for y in range(0, tft.size()[1] + radius, radius * 2):
            tft.circle((x, y), radius, color)

def testtriangles():
    tft.fill(TFT.BLACK);
    color = 0xF800
    w = tft.size()[0] // 2
    x = tft.size()[1] - 1
    y = 0
    z = tft.size()[0]
    for t in range(0, 15):
        tft.line((w, y), (y, x), color)
        tft.line((y, x), (z, x), color)
        tft.line((z, x), (w, y), color)
        x -= 4
        y += 4
        z -= 4
        color += 100

def testroundrects():
    tft.fill(TFT.BLACK);
    color = 100
    for t in range(5):
        x = 0
        y = 0
        w = tft.size()[0] - 2
        h = tft.size()[1] - 2
        for i in range(17):
            tft.rect((x, y), (w, h), color)
            x += 2
            y += 3
            w -= 4
            h -= 6
            color += 1100
        color += 100

def tftprinttest():
    tft.fill(TFT.BLACK);
    v = 30
    tft.text((0, v), "Fuck you!", TFT.RED, sysfont, 1, nowrap=True)
    v += sysfont["Height"]
    tft.text((0, v), "Fuck you!", TFT.YELLOW, sysfont, 2, nowrap=True)
    v += sysfont["Height"] * 2
    tft.text((0, v), "Fuck you!", TFT.GREEN, sysfont, 3, nowrap=True)
    v += sysfont["Height"] * 3
    tft.text((0, v), str(1234.567), TFT.BLUE, sysfont, 4, nowrap=True)
    time.sleep_ms(1500)
    tft.fill(TFT.BLACK);
    v = 0
    tft.text((0, v), "Fuck you!", TFT.RED, sysfont)
    v += sysfont["Height"]
    tft.text((0, v), str(math.pi), TFT.GREEN, sysfont)
    v += sysfont["Height"]
    tft.text((0, v), " Want pi?", TFT.GREEN, sysfont)
    v += sysfont["Height"] * 2
    tft.text((0, v), hex(8675309), TFT.GREEN, sysfont)
    v += sysfont["Height"]
    tft.text((0, v), " Print HEX!", TFT.GREEN, sysfont)
    v += sysfont["Height"] * 2
    tft.text((0, v), "Sketch has been", TFT.WHITE, sysfont)
    v += sysfont["Height"]
    tft.text((0, v), "running for: ", TFT.WHITE, sysfont)
    v += sysfont["Height"]
    tft.text((0, v), str(time.ticks_ms() / 1000), TFT.PURPLE, sysfont)
    v += sysfont["Height"]
    tft.text((0, v), " seconds.", TFT.WHITE, sysfont)

def randomFrame(data, len):
    for x in range(len):            
      data[x] = random.randint(0, 255)

def showBMP():
    f=open('lora.bmp', 'rb')    
    if f.read(2) == b'BM':  #header
        dummy = f.read(8) #file size(4), creator bytes(4)
        offset = int.from_bytes(f.read(4), 'little')
        hdrsize = int.from_bytes(f.read(4), 'little')
        width = int.from_bytes(f.read(4), 'little')
        height = int.from_bytes(f.read(4), 'little')
        if int.from_bytes(f.read(2), 'little') == 1: #planes must be 1
            depth = int.from_bytes(f.read(2), 'little')
            if depth == 24 and int.from_bytes(f.read(4), 'little') == 0:#compress method == uncompressed
                rowsize = (width * 3 + 3) & ~3
                if height < 0:
                    height = -height
                    flip = False
                else:
                    flip = True
                w, h = width, height
                if w > 128: w = 128
                if h > 160: h = 160
                tft._setwindowloc((0,0),(w - 1,h - 1))
                for row in range(h):
                    if flip:
                        pos = offset + (height - 1 - row) * rowsize
                    else:
                        pos = offset + row * rowsize
                    if f.tell() != pos:
                        dummy = f.seek(pos)
                    for col in range(w):
                        bgr = f.read(3)
                        tft._pushcolor(TFTColor(bgr[2],bgr[1],bgr[0]))
    f.close()

def time_lcd(datetime):
    if datetime[4] == 0:
        hours = "00"
    elif datetime[4] < 10:
        hours = "0" + str(datetime[4])
    else:
        hours = str(datetime[4])

    if datetime[5] == 0:
        minutes = "00"
    elif datetime[5] < 10:
        minutes = "0" + str(datetime[5])
    else:
        minutes = str(datetime[5])

    if datetime[6] == 0:
        seconds = "00"
    elif datetime[6] < 10:
        seconds = "0" + str(datetime[6])
    else:
        seconds = str(datetime[6])
    tft.text((0, 20), "{}.{}.{} {}:{}:{}".format(datetime[2], datetime[1], datetime[0], hours, minutes, seconds), TFT.WHITE, sysfont, 1)    

def stat_lcd():
    tft.text((0, 30), "FrmTx: " + str(cntTxFrame), TFT.YELLOW, sysfont, 1)    
    tft.text((0, 40), "FrmRx: " + str(cntRxFrame), TFT.GREEN, sysfont, 1)    
    tft.text((0, 50), "CrcOk: " + str(crcFrameRxCntOk), TFT.GREEN, sysfont, 1)    
    tft.text((0, 60), "CrcEr: " + str(crcFrameRxCntErr), TFT.RED, sysfont, 1)    
    if LoRaMaster:
        tft.text((0, 70), "FrmLost: " + str(cntFrmTout), TFT.RED, sysfont, 1)
        flr = (int)(10000*(cntFrmTout/cntTxFrame))
        tft.text((0, 80), "FLR: " + str(flr/100) + " %   ", TFT.YELLOW, sysfont, 1)
    else:
        if crcFrameRxCntErr + crcFrameRxCntOk > 0:
            cfr = (int)(10000*(crcFrameRxCntErr/(crcFrameRxCntErr + crcFrameRxCntOk)))
            tft.text((0, 70), "CFR: " + str(cfr/100) + " %   ", TFT.YELLOW, sysfont, 1)    
        else:
            tft.text((0, 70), "CFR: 0,00 %   ", TFT.YELLOW, sysfont, 1)
    tft.text((0, 90), "RSSI: " + str(lora.get_rssi()) + " dBm   ", TFT.WHITE, sysfont, 1)    
    tft.text((0, 100), "SNR : " + str(lora.get_snr()) + " dB    ", TFT.WHITE, sysfont, 1)       
    tft.text((0, 110), "Frq : " + str(lora._frequency) + " MHz", TFT.WHITE, sysfont, 1)       
    tft.text((0, 120), "BW  : " + str(lora._bandwidth) + " Hz", TFT.WHITE, sysfont, 1)       
    tft.text((0, 130), "SF  : " + str(lora._sf), TFT.WHITE, sysfont, 1)       
    tft.text((0, 140), "CR  : " + str(lora._cr), TFT.WHITE, sysfont, 1)       
    tft.text((0, 150), "PL  : " + str(lora._pl), TFT.WHITE, sysfont, 1)
        
def write_log(f, datetime):
        f.write("{}.{}.{} {}:{}:{}".format(datetime[2], datetime[1], datetime[0], datetime[4], datetime[5], datetime[6]) + ", FrmTx: " + str(cntTxFrame) + ", FrmRx: " + str(cntRxFrame) + " CrcOk: " + str(crcFrameRxCntOk) + ", CrcEr: " + str(crcFrameRxCntErr) + ", FrmLost: " + str(cntFrmTout) + ", RSSI: " + str(lora.get_rssi()) + " dBm" + ", SNR : " + str(lora.get_snr()) + " dB\n")

def test_main():
    global cntRxFrame, cntTxFrame, lineLCD, LoRaMaster, respFlag, dataFrameRx, crcFrameRxCntOk, crcFrameRxCntErr, logNr, cntFrmTout
    print(TEST_VER_STR)
    print(os.uname())
    fileName = "log{}.txt".format(logNr)
    f = open(fileName, 'wt')
    timer.init(freq=2.5, mode=Timer.PERIODIC, callback=blink)
    showBMP()
    time.sleep_ms(3000) 
    tft.fill(TFT.BLACK)   
    f.write(str(TEST_VER_STR + "\n"))
    tft.text((0, 0), TEST_VER_STR, TFT.WHITE, sysfont, 1)
    if LoRaMaster:
        f.write(str(MASTER_STR + "\n"))
        tft.text((0, 10), MASTER_STR, TFT.GREEN, sysfont, 1)
    else:
        f.write(str(SLAVE_STR + "\n"))
        tft.text((0, 10), SLAVE_STR, TFT.GREEN, sysfont, 1)        
 
    f.write("Frequecy : " + str(lora._frequency) + " MHz" + ", Bandwidth : " + str(lora._bandwidth) + " Hz" + ", SF(spread factor): " + str(lora._sf) + ", CR(Coding Rate): " + str(lora._cr) + ", PL(Preamble Length): " + str(lora._pl) + "\n")
    # Set handler
    lora.on_recv(handler)
    # Put module in recv mode
    if LoRaMaster == 0:
        lora.recv()
    cntFrmOk = 0
    cntFrmTout= 0
    dataFrameTx = bytearray(16)    
    crcFrameTx = Crc()
    crcFrameRx = Crc() 
    while(1):
        
        if LoRaMaster:
            cntTxFrame = cntTxFrame + 1
            randomFrame(dataFrameTx, len(dataFrameTx))
            crcFrameTx.add_crc8(dataFrameTx, len(dataFrameTx))
            lora.send(dataFrameTx)
            lora.recv()
            timeOut = 0
            while ((respFlag == 0) and (timeOut < TIME_OUT_7800_8_8)):
                time.sleep_ms(10)
                timeOut = timeOut + 1
                
            if respFlag:
                respFlag = 0
                cntRxFrame = cntRxFrame + 1
                if (crcFrameRx.check_crc8(dataFrameRx, len(dataFrameRx))):
                    crcFrameRxCntOk = crcFrameRxCntOk + 1
                else:
                    crcFrameRxCntErr = crcFrameRxCntErr + 1
            else:
                cntFrmTout = cntFrmTout + 1
            now = rtc.datetime()
            time_lcd(now)
            stat_lcd()
            write_log(f, now)
            f.close()
            file_stat = os.stat(fileName)
            f = open(fileName, 'at')
            if ((int)(file_stat[6])) > LOG_SIZE_KB*1024:  # maksymalny rozmiar pliku okolo: LOG_SIZE_KB*kB
                f.close()
                logNr = logNr + 1
                if logNr > 7: # pliki z logami od log0..log7 i nadpisanie
                    logNr = 0
                fileName = "log{}.txt".format(logNr)
                f = open(fileName, 'wt')
               
        else:
            now = rtc.datetime()
            time_lcd(now)
            stat_lcd()  
            if respFlag:
                respFlag = 0
                cntRxFrame = cntRxFrame + 1
                if (crcFrameRx.check_crc8(dataFrameRx, len(dataFrameRx))):
                    crcFrameRxCntOk = crcFrameRxCntOk + 1                    
                    randomFrame(dataFrameTx, len(dataFrameTx))
                    crcFrameTx.add_crc8(dataFrameTx, len(dataFrameTx))
                    lora.send(dataFrameTx)
                    lora.recv()
                    cntTxFrame = cntTxFrame + 1           
                else:
                    crcFrameRxCntErr = crcFrameRxCntErr + 1    
                write_log(f, now)
                f.close()
                file_stat = os.stat(fileName)
                f = open(fileName, 'at')
                if ((int)(file_stat[6])) > LOG_SIZE_KB*1024:  # maksymalny rozmiar pliku okolo: LOG_SIZE_KB*kB
                    f.close()
                    logNr = logNr + 1
                    if logNr > 7: # pliki z logami od log0..log7 i nadpisanie
                        logNr = 0
                    fileName = "log{}.txt".format(logNr)
                    f = open(fileName, 'wt')            
 
test_main()




