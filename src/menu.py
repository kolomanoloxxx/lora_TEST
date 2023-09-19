from ST7735 import TFT,TFTColor
from sysfont import sysfont
from machine import RTC
from buzzer import BUZZER
import time
import math
import gc
import os
import loracfg
import keys

def root(tft, button, rtc, bl, bzykacz):
    tft.fill(TFT.BLACK)
    sel = 1
    menu_exit = 1
    while(menu_exit):
        color = [TFT.WHITE, TFT.WHITE, TFT.WHITE, TFT.WHITE, TFT.WHITE, TFT.WHITE, TFT.WHITE, TFT.WHITE, TFT.WHITE, TFT.WHITE]
        color[sel] = TFT.GREEN
        tft.text((0, 0), "Wybierz:", color[0] , sysfont, 1)
        tft.text((0, 10), "LoRa", color[1], sysfont, 1)
        tft.text((0, 20), "Data i Czas", color[2], sysfont, 1)
        tft.text((0, 30), "Podswietlenie", color[3], sysfont, 1)
        tft.text((0, 40), "Bzykacz", color[4], sysfont, 1)
        tft.text((0, 50), "Zapisz konfiguracje", color[5], sysfont, 1)
        tft.text((0, 60), "Pokaz konfiguracje", color[6], sysfont, 1)
        tft.text((0, 70), "Wyjscie", color[7], sysfont, 1)
        
        while(button.read()):
            pass
        key = 0
        while(key == 0):
            key = button.read()
        bzykacz.beep(1)
        if key == 1:
            sel = sel - 1
            if sel == 0:
                sel = 7
        if key == 2:
            sel = sel + 1
            if sel == 8:
                sel = 1  
        if key == 4:
            if (sel == 1):
                lora(tft, button, bzykacz)
            elif (sel == 2):
                date_time(tft, button, rtc, bzykacz)
            elif (sel == 3):
                lcd(tft, button, bl, bzykacz)
            elif (sel == 4):
                buz(tft, button, bl, bzykacz)
            elif (sel == 5):
                save_cfg(tft)
                menu_exit = 0
            elif (sel == 6):
                show_cfg(tft, button, bzykacz)
            else:
                tft.fill(TFT.BLACK)
                menu_exit = 0

def lora(tft, button, bzykacz):
    tft.fill(TFT.BLACK)
    sel = 1
    menu_exit = 1
    while(menu_exit):
        color = [TFT.WHITE, TFT.WHITE, TFT.WHITE, TFT.WHITE, TFT.WHITE, TFT.WHITE, TFT.WHITE, TFT.WHITE, TFT.WHITE]
        color[sel] = TFT.GREEN
        tft.text((0, 0), "Konfiguracja LoRa:", color[0] , sysfont, 1)
        tft.text((0, 10), "Ustaw Master/Slave", color[1], sysfont, 1)
        tft.text((0, 20), "Ustaw czestotliwosc", color[2], sysfont, 1)
        tft.text((0, 30), "Ustaw BW", color[3], sysfont, 1)
        tft.text((0, 40), "Ustaw SF", color[4], sysfont, 1)
        tft.text((0, 50), "Ustaw CR", color[5], sysfont, 1)
        tft.text((0, 60), "Ustaw PL", color[6], sysfont, 1)
        tft.text((0, 70), "Ustaw PPM", color[7], sysfont, 1)
        tft.text((0, 80), "Wyjscie", color[8], sysfont, 1)
        while(button.read()):
            pass
        key = 0
        while(key == 0):
            key = button.read()
        bzykacz.beep(1)            
        if key == 1:
            sel = sel - 1
            if sel == 0:
                sel = 8
        if key == 2:
            sel = sel + 1
            if sel == 9:
                sel = 1  
        if key == 4:
            if (sel == 8):
                menu_exit = 0
                tft.fill(TFT.BLACK)

            else:    
                lora_set(tft, sel, button, bzykacz)

def lora_set(tft, sel, button, bzykacz):
    if (sel == 1):
        master = loracfg.cfg["MASTER"]
        menu_exit = 1
        while (menu_exit):
            tft.fill(TFT.BLACK)
            tft.text((0, 0), "Zmiana:", TFT.WHITE , sysfont, 1)
            if master:
                tft.text((0, 10), "Master", TFT.GREEN, sysfont, 1)
            else:
                tft.text((0, 10), "Slave ", TFT.GREEN, sysfont, 1)
            while(button.read()):
                pass
            key = 0
            while(key == 0):
                key = button.read()
            bzykacz.beep(1)            
            if key == 1:
                master = not(master)
            if key == 2:
                master = not(master)
            if key == 4:
                loracfg.cfg["MASTER"] = int(master)
                menu_exit = 0
                tft.fill(TFT.BLACK)

    if (sel == 2):
        freq = loracfg.cfg["FRQ"]
        menu_exit = 1
        while (menu_exit):
            tft.fill(TFT.BLACK)
            tft.text((0, 0), "Zmiana:", TFT.WHITE , sysfont, 1)
            tft.text((0, 10), "Freq: ", TFT.WHITE, sysfont, 1)
            tft.text((50, 10), str(freq), TFT.GREEN, sysfont, 1)
            while(button.read()):
                pass
            key = 0
            while(key == 0):
                key = button.read()
            bzykacz.beep(1)
            if key == 1:
                freq = freq+1
                if (freq > 525):
                    freq = 410
            if key == 2:
                freq = freq-1
                if (freq < 410):
                    freq = 525
            if key == 4:
                loracfg.cfg["FRQ"] = freq
                menu_exit = 0
                tft.fill(TFT.BLACK)

    if (sel == 3):
        bw = loracfg.cfg["BW"]
        bws = (7800, 10400, 15600, 20800, 31250, 41700, 62500, 125000, 250000, 500000)
        for j in range(9):
            if bw == bws[j]:
                break
        menu_exit = 1
        while (menu_exit):
            tft.fill(TFT.BLACK)
            tft.text((0, 0), "Zmiana:", TFT.WHITE , sysfont, 1)
            tft.text((0, 10), "BW: ", TFT.WHITE, sysfont, 1)
            tft.text((50, 10), str(bw)+"   ", TFT.GREEN, sysfont, 1)
            while(button.read()):
                pass
            key = 0
            while(key == 0):
                key = button.read()
            bzykacz.beep(1)            
            if key == 1:
                j = j+1
                if (j > 9):
                    j = 0
            if key == 2:
                j = j-1
                if (j < 0):
                    j = 9
            if key == 4:
                loracfg.cfg["BW"] = bws[j]
                menu_exit = 0
                tft.fill(TFT.BLACK)

            bw = bws[j]                
    if (sel == 4):
        sf = loracfg.cfg["SF"]
        menu_exit = 1
        while (menu_exit):
            tft.fill(TFT.BLACK)
            tft.text((0, 0), "Zmiana:", TFT.WHITE , sysfont, 1)
            tft.text((0, 10), "SF: ", TFT.WHITE, sysfont, 1)
            tft.text((50, 10), str(sf)+"   ", TFT.GREEN, sysfont, 1)
            while(button.read()):
                pass            
            key = 0
            while(key == 0):
                key = button.read()
            bzykacz.beep(1)            
            if key == 1:
                sf = sf+1
                if (sf > 12):
                    sf = 6
            if key == 2:
                sf = sf-1
                if (sf < 6):
                    sf = 12
            if key == 4:
                loracfg.cfg["SF"] = sf
                menu_exit = 0
                tft.fill(TFT.BLACK)

    if (sel == 5):
        cr = loracfg.cfg["CR"]
        menu_exit = 1
        while (menu_exit):
            tft.fill(TFT.BLACK)
            tft.text((0, 0), "Zmiana:", TFT.WHITE , sysfont, 1)
            tft.text((0, 10), "CR: ", TFT.WHITE, sysfont, 1)
            tft.text((50, 10), str(cr), TFT.GREEN, sysfont, 1)
            while(button.read()):
                pass            
            key = 0
            while(key == 0):
                key = button.read()
            bzykacz.beep(1)            
            if key == 1:
                cr = cr+1
                if (cr > 8):
                    cr = 5
            if key == 2:
                cr = cr-1
                if (cr < 5):
                    cr = 8
            if key == 4:
                loracfg.cfg["CR"] = cr
                menu_exit = 0
                tft.fill(TFT.BLACK)

    if (sel == 6):
        pl = loracfg.cfg["PL"]
        menu_exit = 1
        while (menu_exit):
            tft.fill(TFT.BLACK)
            tft.text((0, 0), "Zmiana:", TFT.WHITE , sysfont, 1)
            tft.text((0, 10), "PL: ", TFT.WHITE, sysfont, 1)
            tft.text((50, 10), str(pl)+"   ", TFT.GREEN, sysfont, 1)
            while(button.read()):
                pass
            key = 0
            while(key == 0):
                key = button.read()
            bzykacz.beep(1)            
            if key == 1:
                pl = pl+1
                if (pl > 65000):
                    pl = 65000
            if key == 2:
                pl = pl-1
                if (pl < 1):
                    pl = 1
            if key == 4:
                loracfg.cfg["PL"] = pl
                menu_exit = 0
                tft.fill(TFT.BLACK)    

    if (sel == 7):
        ppm = loracfg.cfg["PPM"]
        menu_exit = 1
        while (menu_exit):
            tft.fill(TFT.BLACK)
            tft.text((0, 0), "Zmiana:", TFT.WHITE , sysfont, 1)
            tft.text((0, 10), "PPM: ", TFT.WHITE, sysfont, 1)
            tft.text((50, 10), str(ppm)+"   ", TFT.GREEN, sysfont, 1)
            while(button.read()):
                pass
            key = 0
            while(key == 0):
                key = button.read()
            bzykacz.beep(1)
            if key == 1:
                ppm = ppm+1
                if (ppm > 127):
                    ppm = 127
            if key == 2:
                ppm = ppm-1
                if (ppm < -127):
                    ppm = -127
            if key == 4:
                loracfg.cfg["PPM"] = ppm
                menu_exit = 0
                tft.fill(TFT.BLACK)

def save_cfg(tft):
    tft.fill(TFT.BLACK)
    tft.text((0, 0), "Konfiguracja zapisana", TFT.WHITE , sysfont, 1)
    loracfg.write()
    time.sleep_ms(3000)  
    tft.fill(TFT.BLACK)

def show_cfg(tft, button, bzykacz):
    menu_exit = 1
    while (menu_exit):
        tft.fill(TFT.BLACK)
        tft.text((0, 0), "Konfiguracja:", TFT.WHITE , sysfont, 1)
        tft.text((0, 10), "Tryb: {}".format(loracfg.cfg["MASTER"]), TFT.WHITE, sysfont, 1)
        tft.text((0, 20), "FRQ : {}".format(loracfg.cfg["FRQ"]), TFT.WHITE, sysfont, 1)
        tft.text((0, 30), "BW  : {}".format(loracfg.cfg["BW"]), TFT.WHITE, sysfont, 1)
        tft.text((0, 40), "SF  : {}".format(loracfg.cfg["SF"]), TFT.WHITE, sysfont, 1)
        tft.text((0, 50), "CR  : {}".format(loracfg.cfg["CR"]), TFT.WHITE, sysfont, 1)
        tft.text((0, 60), "PL  : {}".format(loracfg.cfg["PL"]), TFT.WHITE, sysfont, 1)
        tft.text((0, 70), "PPM : {}".format(loracfg.cfg["PPM"]), TFT.WHITE, sysfont, 1)
        tft.text((0, 80), "LCD : {}".format(loracfg.cfg["LCD"]), TFT.WHITE, sysfont, 1)
        tft.text((0, 90), "BUZ : {}".format(loracfg.cfg["BUZ"]), TFT.WHITE, sysfont, 1)
        while(button.read()):
            pass
        key = 0
        while(key == 0):
            key = button.read()
        bzykacz.beep(1)            
        if key == 4:
            menu_exit = 0
            tft.fill(TFT.BLACK)

def date_time(tft, button, rtc, bzykacz):
    tft.fill(TFT.BLACK)
    sel = 1
    menu_exit = 1
    while(menu_exit):
        color = [TFT.WHITE, TFT.WHITE, TFT.WHITE, TFT.WHITE]
        color[sel] = TFT.GREEN
        tft.text((0, 0), "Ustawienie daty i czasu:", color[0] , sysfont, 1)
        tft.text((0, 10), "Data", color[1], sysfont, 1)
        tft.text((0, 20), "Czas", color[2], sysfont, 1)
        tft.text((0, 30), "Wyjscie", color[3], sysfont, 1)
        while(button.read()):
            pass
        key = 0
        while(key == 0):
            key = button.read()
        bzykacz.beep(1)    
        if key == 1:
            sel = sel - 1
            if sel == 0:
                sel = 3
        if key == 2:
            sel = sel + 1
            if sel == 4:
                sel = 1  
        if key == 4:
            if (sel == 1):
                date_set(tft, button, rtc, bzykacz)
            elif (sel == 2):
                time_set(tft, button, rtc, bzykacz)
            else:
                menu_exit = 0
                tft.fill(TFT.BLACK)


def date_set(tft, button, rtc, bzykacz):
    tft.fill(TFT.BLACK)
    datetime = rtc.datetime()
    dzien = int(datetime[2])
    miesiac = int(datetime[1])
    rok = int(datetime[0])
    sel = 1
    menu_exit = 1
    while(menu_exit):
        color = [TFT.WHITE, TFT.WHITE, TFT.WHITE, TFT.WHITE, TFT.WHITE]
        color[sel] = TFT.GREEN
        tft.text((0, 0), "Ustawienie daty:", color[0] , sysfont, 1)
        if (dzien<10):        
            tft.text((0, 10), "0{}".format(dzien), color[1], sysfont, 1)
        else:
            tft.text((0, 10), "{}".format(dzien), color[1], sysfont, 1)
        tft.text((12, 10), ".", TFT.WHITE, sysfont, 1)
        if (miesiac<10):                
            tft.text((18, 10), "0{}".format(miesiac), color[2], sysfont, 1)
        else:
            tft.text((18, 10), "{}".format(miesiac), color[2], sysfont, 1)
        tft.text((30, 10), ".", TFT.WHITE, sysfont, 1)    
        tft.text((36, 10), "{}".format(rok), color[3], sysfont, 1)    
        tft.text((0, 20), "Zapisz", color[4] , sysfont, 1)
        
        while(button.read()):
            pass
        key = 0
        while(key == 0):
            key = button.read()
        bzykacz.beep(1)
        if key == 1:
            if sel == 1:
                dzien = dzien + 1
                if (dzien>31):
                    dzien = 31
            if sel == 2:
                miesiac = miesiac + 1
                if (miesiac>12):
                    miesiac = 12
            if sel == 3:
                rok = rok + 1
                if (rok>2050):
                    rok = 2050
            if sel == 4:
              menu_exit = 0
              rtc.datetime((rok, miesiac, dzien, datetime[3], datetime[4], datetime[5], datetime[6], datetime[7]))          
              tft.fill(TFT.BLACK)

        if key == 2:
            if sel == 1:
                dzien = dzien - 1
                if (dzien<1):
                    dzien = 1
            if sel == 2:
                miesiac = miesiac - 1
                if (miesiac<1):
                    miesiac = 1
            if sel == 3:
                rok = rok - 1
                if (rok<2000):
                    rok = 2000
            if sel == 4:
                menu_exit = 0
                rtc.datetime((rok, miesiac, dzien, datetime[3], datetime[4], datetime[5], datetime[6], datetime[7]))          
                tft.fill(TFT.BLACK)
    
        if key == 4:
            sel = sel + 1
            if sel == 5:
                sel = 1
                
def time_set(tft, button, rtc, bzykacz):
    tft.fill(TFT.BLACK)
    datetime = rtc.datetime()
    godzina = 0
    minuta = 0
    sekunda = 0
    sel = 1
    menu_exit = 1
    while(menu_exit):
        color = [TFT.WHITE, TFT.WHITE, TFT.WHITE, TFT.WHITE, TFT.WHITE]
        color[sel] = TFT.GREEN
        tft.text((0, 0), "Ustawienie czasu:", color[0] , sysfont, 1)
        if (godzina<10):        
            tft.text((0, 10), "0{}".format(godzina), color[1], sysfont, 1)
        else:
            tft.text((0, 10), "{}".format(godzina), color[1], sysfont, 1)
        tft.text((12, 10), ":", TFT.WHITE, sysfont, 1)
        if (minuta<10):                
            tft.text((18, 10), "0{}".format(minuta), color[2], sysfont, 1)
        else:
            tft.text((18, 10), "{}".format(minuta), color[2], sysfont, 1)
        tft.text((30, 10), ":", TFT.WHITE, sysfont, 1)    
        if (sekunda<10):                
            tft.text((36, 10), "0{}".format(sekunda), color[3], sysfont, 1)
        else:
            tft.text((36, 10), "{}".format(sekunda), color[3], sysfont, 1)
        tft.text((0, 20), "Zapisz", color[4] , sysfont, 1)
        
        while(button.read()):
            pass
        key = 0
        while(key == 0):
            key = button.read()
        bzykacz.beep(1)
        if key == 1:
            if sel == 1:
                godzina = godzina + 1
                if (godzina>23):
                    godzina = 0
            if sel == 2:
                minuta = minuta + 1
                if (minuta>59):
                    minuta = 0
            if sel == 3:
                sekunda = sekunda + 1
                if (sekunda>59):
                    sekunda = 0
            if sel == 4:
              menu_exit = 0
              rtc.datetime((datetime[0], datetime[1], datetime[2], godzina, minuta, sekunda, datetime[6], datetime[7]))              
              tft.fill(TFT.BLACK)

        if key == 2:
            if sel == 1:
                godzina = godzina - 1
                if (godzina<0):
                    godzina = 23
            if sel == 2:
                minuta = minuta - 1
                if (minuta<0):
                    minuta = 59
            if sel == 3:
                sekunda = sekunda - 1
                if (sekunda<0):
                    sekunda = 59
            if sel == 4:
                menu_exit = 0
                rtc.datetime((datetime[0], datetime[1], datetime[2], godzina, minuta, sekunda, datetime[6], datetime[7]))              
                tft.fill(TFT.BLACK)
    
        if key == 4:
            sel = sel + 1
            if sel == 5:
                sel = 1
    
def lcd(tft, button, bl, bzykacz):
    tft.fill(TFT.BLACK)
    jasnosc = loracfg.cfg["LCD"]    
    sel = 1
    menu_exit = 1
    while(menu_exit):
        tft.text((0, 0), "Regulacja podswietlenia", TFT.WHITE , sysfont, 1)
        if (jasnosc==100):                
            tft.text((15, 10), "{}%".format(jasnosc), TFT.GREEN, sysfont, 1)
        elif (jasnosc<10):                
            tft.text((15, 10), "  {}%".format(jasnosc), TFT.GREEN, sysfont, 1)
        else:
            tft.text((15, 10), " {}%".format(jasnosc), TFT.GREEN, sysfont, 1)
        while(button.read()):
            pass
        key = 0
        while(key == 0):
            key = button.read()
        bzykacz.beep(1)
        if key == 1:
            jasnosc = jasnosc + 1
            if jasnosc == 101:
                jasnosc = 100
        if key == 2:
            jasnosc = jasnosc - 1
            if jasnosc < 0:
                jasnosc = 0  
        if key == 4:
            menu_exit = 0
            loracfg.cfg["LCD"] = jasnosc            
            tft.fill(TFT.BLACK)
        bl.duty_u16(int((jasnosc/100)*65535))

def buz(tft, button, bl, bzykacz):
    tft.fill(TFT.BLACK)
    buzOnOff = loracfg.cfg["BUZ"]    
    menu_exit = 1
    while (menu_exit):
        tft.fill(TFT.BLACK)
        tft.text((0, 0), "Wlacznik bzykacza:", TFT.WHITE , sysfont, 1)
        if buzOnOff:
            tft.text((0, 10), "On ", TFT.GREEN, sysfont, 1)
        else:
            tft.text((0, 10), "Off ", TFT.GREEN, sysfont, 1)
        while(button.read()):
            pass
        key = 0
        while(key == 0):
            key = button.read()
        bzykacz.beep(1)            
        if key == 1:
            buzOnOff = not(buzOnOff)
        if key == 2:
            buzOnOff = not(buzOnOff)
        if key == 4:
            loracfg.cfg["BUZ"] = int(buzOnOff)
            menu_exit = 0
            tft.fill(TFT.BLACK)
