import time
from machine import Pin, PWM

class BUZZER:
  def __init__(self):
    self.buzzer = Pin(8, Pin.OUT)    
    self.buzzer.high()

  def sound(self, freq, vol):
    self._freq = freq
    self._vol = vol
    self.buzzer = PWM(Pin(8))
    self.buzzer.freq(self._freq)
    self.buzzer.duty_u16(int((self._vol/1000)*65535))
    
  def off(self):
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
        time.sleep_ms(msTime)    
        self.buzzer.high()
        
  def StarWars(self):
    #TODO
    pass
