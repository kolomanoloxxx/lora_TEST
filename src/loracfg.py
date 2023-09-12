import os
import json

cfg = {
              "NAME": "LoRaCFG",
              "MASTER": 1,
              "FRQ": 433,
              "BW": 125000,
              "SF": 12,
              "CR": 8,
              "PL": 64,
              "PPM": 0,
              "LCD": 90,
              "BUZ": 0
      }

def init():
    global cfg
    try:
        f = open("loracfg.txt", 'rt')
    except:
        try:
            f = open("loracfg.txt", 'wt')
        except:
            print("LoRa config Error")
        else:
            f.write("{\"NAME\": \"LoRaCFG\",\n")
            f.write("\"MASTER\": 1,\n")            
            f.write("\"FRQ\": 410,\n")
            f.write("\"BW\": 7800,\n")
            f.write("\"SF\": 8,\n")
            f.write("\"CR\": 8,\n")
            f.write("\"PL\": 64,\n")
            f.write("\"PPM\": 0,\n")
            f.write("\"LCD\": 90,\n")
            f.write("\"BUZ\": 1}")
            f.close()
    else:
        data = f.read()
        cfg = json.loads(data)
        f.close()

def write():
    global cfg
    try:
        f = open("loracfg.txt", 'wt')
    except:
        print("LoRa config Error")
    else:
        f.write("{\"NAME\": \"LoRaCFG\",\n")
        f.write(str("\"MASTER\": {},\n".format(cfg["MASTER"])))            
        f.write(str("\"FRQ\": {},\n".format(cfg["FRQ"])))
        f.write(str("\"BW\": {},\n".format(cfg["BW"])))
        f.write(str("\"SF\": {},\n".format(cfg["SF"])))                             
        f.write(str("\"CR\": {},\n".format(cfg["CR"]))) 
        f.write(str("\"PL\": {},\n".format(cfg["PL"]))) 
        f.write(str("\"PPM\": {},\n".format(cfg["PPM"]))) 
        f.write(str("\"LCD\": {},\n".format(cfg["LCD"]))) 
        f.write(str("\"BUZ\": {},\n".format(cfg["BUZ"]))) 
        f.write(str("}\n")) 
        f.close()
        

