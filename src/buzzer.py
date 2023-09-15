import utime
from machine import Pin, PWM
from utime import sleep, sleep_ms

class BUZZER:
    #initialize all the notes
    c = 261
    d = 294
    e = 329
    f = 349
    g = 391
    gS = 415
    a = 440
    aS = 455
    b = 466
    cH = 523
    cSH = 554
    dH = 587
    dSH = 622
    eH = 659
    fH = 698
    fSH = 740
    gH = 784
    gSH = 830
    aH = 880
    def __init__(self):
        self.buzzer = Pin(8, Pin.OUT)    
        self.buzzer.high()

    def sound(self, freq, vol):
        self._freq = freq
        self._vol = vol
        self.buzzer = PWM(Pin(8))
        self.buzzer.freq(self._freq)
        self.buzzer.duty_u16(int((self._vol/1000)*65535))
    
    def off(self, enable = 0):
        if (enable):
            self.buzzer = Pin(8, Pin.OUT)    
            self.buzzer.high()

    def rx(self, enable):
        if (enable):
            self.sound(8,990)

    def tx(self, enable):
        if (enable):
            self.sound(80,970)

    def beep(self, enable, msTime=10):
        if (enable):
            self.buzzer = Pin(8, Pin.OUT)    
            self.buzzer.low()
            utime.sleep_ms(msTime)    
            self.buzzer.high()
        
    def StarWars(self):

        self.starWarsSec1()
        self.starWarsSec2()
        self.starWarsSec3()
        self.starWarsSec2()
        self.starWarsSec4()

    def starWarsBeep(self, note, timeOut):
        corrTime = (timeOut + (note - self.c))/1.5
        vol = 950
        self.sound(note, vol)
        utime.sleep_ms(int(corrTime))
        self.buzzer = Pin(8, Pin.OUT)    
        self.buzzer.high()
        utime.sleep_ms(50)

    def starWarsSec1(self):
  
        self.starWarsBeep(self.a, 500)
        self.starWarsBeep(self.a, 500)   
        self.starWarsBeep(self.a, 500)
        self.starWarsBeep(self.f, 350)
        self.starWarsBeep(self.cH, 100) 
        self.starWarsBeep(self.a, 500)
        self.starWarsBeep(self.f, 350)
        self.starWarsBeep(self.cH, 100)
        self.starWarsBeep(self.a, 650)

        utime.sleep_ms(500) 

        self.starWarsBeep(self.eH, 400)
        self.starWarsBeep(self.eH, 400)
        self.starWarsBeep(self.eH, 400)  
        self.starWarsBeep(self.fH, 200)
        self.starWarsBeep(self.cH, 100)
        self.starWarsBeep(self.gS, 500)
        self.starWarsBeep(self.f, 350)
        self.starWarsBeep(self.cH, 150)
        self.starWarsBeep(self.a, 650)

        utime.sleep_ms(500) 

    def starWarsSec2(self):
  
        self.starWarsBeep(self.aH, 250)
        self.starWarsBeep(self.a, 150)
        self.starWarsBeep(self.a, 150)
        self.starWarsBeep(self.aH, 250)
        self.starWarsBeep(self.gSH, 80)
        self.starWarsBeep(self.gH, 5)
        self.starWarsBeep(self.fSH, 1)
        self.starWarsBeep(self.fH, 1)    
        self.starWarsBeep(self.fSH, 120)

        utime.sleep_ms(325)

        self.starWarsBeep(self.aS, 250)
        self.starWarsBeep(self.dSH, 500)
        self.starWarsBeep(self.dH, 325)  
        self.starWarsBeep(self.cSH, 175)  
        self.starWarsBeep(self.cH, 125)  
        self.starWarsBeep(self.b, 125)  
        self.starWarsBeep(self.cH, 250)  

        utime.sleep_ms(350)

    def starWarsSec3(self):

        self.starWarsBeep(self.f, 250)  
        self.starWarsBeep(self.gS, 500)  
        self.starWarsBeep(self.f, 350) 
        self.starWarsBeep(self.a, 125)
        self.starWarsBeep(self.cH, 500)
        self.starWarsBeep(self.a, 375)  
        self.starWarsBeep(self.cH, 125)
        self.starWarsBeep(self.eH, 650)

        utime.sleep_ms(500)

    def starWarsSec4(self):
  
        self.starWarsBeep(self.f, 250)  
        self.starWarsBeep(self.gS, 500)  
        self.starWarsBeep(self.f, 375) 
        self.starWarsBeep(self.cH, 125)
        self.starWarsBeep(self.a, 500)  
        self.starWarsBeep(self.f, 375)
        self.starWarsBeep(self.cH, 125)
        self.starWarsBeep(self.a, 650)
        
        utime.sleep_ms(650)
