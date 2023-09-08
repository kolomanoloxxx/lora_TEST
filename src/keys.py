import time
from machine import Pin

class KEYS:
  def __init__(self):
      self.key_up = Pin(21, Pin.IN, Pin.PULL_UP)
      self.key_down = Pin(20, Pin.IN, Pin.PULL_UP)
      self.key_ok = Pin(19, Pin.IN, Pin.PULL_UP)

  def read(self):
    batony = 0
    upDebounce = 0
    downDebounce = 0
    okDebounce = 0
    for x in range(8):
      upDebounce <<= 1
      downDebounce <<= 1
      okDebounce <<= 1
      if (bool(self.key_up.value()) == 0):
          upDebounce |= 0x01

      if (bool(self.key_down.value()) == 0):
          downDebounce |= 0x01

      if (bool(self.key_ok.value()) == 0):
          okDebounce |= 0x01

    if (upDebounce == 0xFF):
        batony |= 1
    if (downDebounce == 0xFF):
        batony |= 2
    if (okDebounce == 0xFF):
        batony |= 4
    return (batony)

