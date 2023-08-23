from lora import LoRa
from ST7735 import TFT,TFTColor
from sysfont import sysfont
from machine import SPI,Pin
from machine import Pin, Timer, PWM
import time
import math
import gc

LoRaMaster = 1

cntRxFrame = 0
cntTxFrame = 0
lineLCD = 0
respFlag = 0

# reset do lora RA02 na SX1278
# dokumentacja chinska z dupy wyjeta
# brak opisu do sterowania resetem kiedy aktywny i na jaki czas musi byc aktywny zeby wywylac reset tego badziewia
# eksperymetalnie wydedukowano reset aktywny 0 na min 100 ms kurwa, kurwa, kurwa...chinskie zjeby
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

loraResetPin.low()
time.sleep_ms(100)
loraResetPin.high()
time.sleep_ms(100)

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
    frequency=433.0,
    bandwidth=250000,
    spreading_factor=10,
    coding_rate=5,
)

# Receive handler
def handler(x):
    global cntRxFrame, cntTxFrame, LoRaMaster, respFlag
    cntRxFrame = cntRxFrame + 1
    if LoRaMaster == 0:
        lora.send("Resp->" + str(x))
        cntTxFrame = cntTxFrame + 1        
        lora.recv()
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
                print("Image size:", width, "x", height)
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
def test_main():
    global cntRxFrame, cntTxFrame, lineLCD, LoRaMaster, respFlag
    timer.init(freq=2.5, mode=Timer.PERIODIC, callback=blink)
    showBMP()
    time.sleep_ms(3000) 
    tft.fill(TFT.BLACK)
    tft.text((0, 0), "Test LoRa", TFT.WHITE, sysfont, 1)
    tft.text((0, 10), "wersja: 1.00", TFT.WHITE, sysfont, 1)
    tft.text((0, 20), "by JC 2023.08.23", TFT.WHITE, sysfont, 1)
    tft.text((0, 30), "LoRa SX1278 na SPI0", TFT.WHITE, sysfont, 1)
    tft.text((0, 40), "LCD ST7735 na SPI1", TFT.WHITE, sysfont, 1)
    tft.text((0, 50), "PI PICO 2040", TFT.WHITE, sysfont, 1)
    tft.text((0, 60), "microPytone", TFT.WHITE, sysfont, 1)
    if LoRaMaster:
        tft.text((0, 70), "LoRa Master", TFT.GREEN, sysfont, 1)
    else:
        tft.text((0, 70), "LoRa Slave", TFT.GREEN, sysfont, 1)        
    time.sleep_ms(5000)
    
    # Set handler
    lora.on_recv(handler)
    # Put module in recv mode
    if LoRaMaster == 0:
        lora.recv()
    
    cntFrmOk = 0
    cntFrmTout= 0

    while(1):
        if LoRaMaster:
            cntTxFrame = cntTxFrame + 1

            lora.send("Req-> " + str(cntTxFrame))
            lora.recv()
            
            timeOut = 0
            while ((respFlag == 0) and (timeOut < 100)):
                time.sleep_ms(10)
                timeOut = timeOut + 1
                
            if respFlag:
                cntFrmOk = cntFrmOk + 1
                respFlag = 0
            else:
                cntFrmTout = cntFrmTout + 1

            tft.text((0, 80), "FrmAck : " + str(cntFrmOk), TFT.GREEN, sysfont, 1)    
            tft.text((0, 90), "FrmLost: " + str(cntFrmTout), TFT.RED, sysfont, 1)
            flr = (int)(10000*(cntFrmTout/cntTxFrame))
            tft.text((0, 100), "FLR: " + str(flr/100) + " %   ", TFT.YELLOW, sysfont, 1)    

        else:
            tft.text((0, 80), "FrmRx: " + str(cntRxFrame), TFT.GREEN, sysfont, 1)    
            tft.text((0, 90), "FrmTx: " + str(cntTxFrame), TFT.YELLOW, sysfont, 1)    
            time.sleep_ms(200)
                            
 
test_main()



