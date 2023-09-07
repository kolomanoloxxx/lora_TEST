from ST7735 import TFT,TFTColor
from sysfont import sysfont
import time
import math
import gc
import os
import loracfg

def root(tft):
    sel = 1
    menu_exit = 1
    while(menu_exit):
        color = [TFT.WHITE, TFT.WHITE, TFT.WHITE, TFT.WHITE, TFT.WHITE, TFT.WHITE, TFT.WHITE, TFT.WHITE, TFT.WHITE, TFT.WHITE]
        color[sel] = TFT.GREEN
        tft.fill(TFT.BLACK)
        tft.text((0, 0), "Wybierz:", color[0] , sysfont, 1)
        tft.text((0, 10), "Ustaw Master/Slave", color[1], sysfont, 1)
        tft.text((0, 20), "Ustaw czestotliwosc", color[2], sysfont, 1)
        tft.text((0, 30), "Ustaw BW", color[3], sysfont, 1)
        tft.text((0, 40), "Ustaw SF", color[4], sysfont, 1)
        tft.text((0, 50), "Ustaw CR", color[5], sysfont, 1)
        tft.text((0, 60), "Ustaw date", color[6], sysfont, 1)
        tft.text((0, 70), "Ustaw czas", color[7], sysfont, 1)
        tft.text((0, 80), "Zapisz konfiguracje", color[8], sysfont, 1)
        tft.text((0, 90), "Wyjscie", color[9], sysfont, 1)
        ## narazie klawisze z REPL
        ## docelowo 3 przyciski podlaczone do portow
        key = input("Select:")
        if key == "q":
            sel = sel - 1
            if sel == 0:
                sel = 9
        if key == "a":
            sel = sel + 1
            if sel == 10:
                sel = 1  
        if key == "z":
            if (sel == 8):
                save_cfg(tft)
                menu_exit = 0
            elif (sel == 9):
                menu_exit = 0
            else:    
                change(tft, sel)
        time.sleep_ms(100) 

def change(tft, sel):
    if (sel == 1):
        master = 1
        menu_exit = 1
        while (menu_exit):
            tft.fill(TFT.BLACK)
            tft.text((0, 0), "Wybierz:", TFT.WHITE , sysfont, 1)
            if master:
                tft.text((0, 10), "Master", TFT.GREEN, sysfont, 1)
            else:
                tft.text((0, 10), "Slave", TFT.GREEN, sysfont, 1)
            tft.text((0, 20), "z. Zapis", TFT.GREEN, sysfont, 1)
            key = input("Select:")
            if key == "q":
                master = not(master)
            if key == "a":
                master = not(master)
            if key == "z":
                loracfg.cfg["MASTER"] = master
                menu_exit = 0
            time.sleep_ms(100)    
    if (sel == 2):
        freq = loracfg.cfg["FRQ"]
        menu_exit = 1
        while (menu_exit):
            tft.fill(TFT.BLACK)
            tft.text((0, 0), "Wybierz:", TFT.WHITE , sysfont, 1)
            tft.text((0, 10), "Freq: ", TFT.WHITE, sysfont, 1)
            tft.text((50, 10), str(freq), TFT.GREEN, sysfont, 1)
            tft.text((0, 20), "z. Zapis", TFT.GREEN, sysfont, 1)
            key = input("Select:")
            if key == "q":
                freq = freq-1
                if (freq < 410):
                    freq = 525
            if key == "a":
                freq = freq+1
                if (freq > 525):
                    freq = 410
            if key == "z":
                loracfg.cfg["FRQ"] = freq
                menu_exit = 0
            time.sleep_ms(100)
    if (sel == 3):
        bw = loracfg.cfg["BW"]
        bws = (7800, 10400, 15600, 20800, 31250, 41700, 62500, 125000, 250000, 500000)
        for j in range(9):
            if bw == bws[j]:
                break
        menu_exit = 1
        while (menu_exit):
            tft.fill(TFT.BLACK)
            tft.text((0, 0), "Wybierz:", TFT.WHITE , sysfont, 1)
            tft.text((0, 10), "BW: ", TFT.WHITE, sysfont, 1)
            tft.text((50, 10), str(bw), TFT.GREEN, sysfont, 1)
            tft.text((0, 20), "z. Zapis", TFT.GREEN, sysfont, 1)
            key = input("Select:")
            if key == "q":
                j = j+1
                if (j > 9):
                    j = 0
            if key == "a":
                j = j-1
                if (j < 0):
                    j = 9
            if key == "z":
                loracfg.cfg["BW"] = bws[j]
                menu_exit = 0
            bw = bws[j]                
            time.sleep_ms(100)
    if (sel == 4):
        sf = loracfg.cfg["SF"]
        menu_exit = 1
        while (menu_exit):
            tft.fill(TFT.BLACK)
            tft.text((0, 0), "Wybierz:", TFT.WHITE , sysfont, 1)
            tft.text((0, 10), "SF: ", TFT.WHITE, sysfont, 1)
            tft.text((50, 10), str(sf), TFT.GREEN, sysfont, 1)
            tft.text((0, 20), "z. Zapis", TFT.GREEN, sysfont, 1)
            key = input("Select:")
            if key == "q":
                sf = sf+1
                if (sf > 12):
                    sf = 6
            if key == "a":
                sf = sf-1
                if (sf < 6):
                    sf = 12
            if key == "z":
                loracfg.cfg["SF"] = sf
                menu_exit = 0               
            time.sleep_ms(100)
    if (sel == 5):
        cr = loracfg.cfg["CR"]
        menu_exit = 1
        while (menu_exit):
            tft.fill(TFT.BLACK)
            tft.text((0, 0), "Wybierz:", TFT.WHITE , sysfont, 1)
            tft.text((0, 10), "CR: ", TFT.WHITE, sysfont, 1)
            tft.text((50, 10), str(cr), TFT.GREEN, sysfont, 1)
            tft.text((0, 20), "z. Zapis", TFT.GREEN, sysfont, 1)
            key = input("Select:")
            if key == "q":
                cr = cr+1
                if (cr > 8):
                    cr = 5
            if key == "a":
                cr = cr-1
                if (cr < 5):
                    cr = 8
            if key == "z":
                loracfg.cfg["CR"] = cr
                menu_exit = 0               
            time.sleep_ms(100)
    if (sel == 6):
        menu_exit = 1
        while (menu_exit):
            tft.fill(TFT.BLACK)
            tft.text((0, 0), "Wybierz:", TFT.WHITE , sysfont, 1)
            tft.text((0, 20), "z. Zapis", TFT.GREEN, sysfont, 1)
            key = input("Select:")
            ## TODO
            if key == "z":
                menu_exit = 0               
            time.sleep_ms(100)
    if (sel == 7):
        menu_exit = 1
        while (menu_exit):
            tft.fill(TFT.BLACK)
            tft.text((0, 0), "Wybierz:", TFT.WHITE , sysfont, 1)
            tft.text((0, 20), "z. Zapis", TFT.GREEN, sysfont, 1)
            key = input("Select:")
            ## TODO
            if key == "z":
                loracfg.write()
                menu_exit = 0               
            time.sleep_ms(100)

def save_cfg(tft):
    tft.fill(TFT.BLACK)
    tft.text((0, 0), "Konfiguracja zapisana", TFT.WHITE , sysfont, 1)
    ##TODO
    ##docelowo konfiguracja przechowywana w pliku
    time.sleep_ms(3000)  
