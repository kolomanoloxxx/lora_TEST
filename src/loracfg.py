import os
import json

cfg = {
              "NAME": "LoRaCFG",
              "MASTER": 1,
              "FRQ": 410,
              "BW": 7800,
              "SF": 8,
              "CR": 8,
              "PL": 64
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
            f.write("\"MASSTER\": 1,\n")            
            f.write("\"FRQ\": 410,\n")
            f.write("\"BW\": 7800,\n")
            f.write("\"SF\": 8,\n")
            f.write("\"CR\": 8,\n")
            f.write("\"PL\": 64}")
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
        f.write(str("\"MASSTER\": {},\n".format(cfg["MASTER"])))            
        f.write(str("\"FRQ\": {},\n".format(cfg["FRQ"])))
        f.write("\"BW\": 7800,\n")
        f.write("\"SF\": 8,\n")
        f.write("\"CR\": 8,\n")
        f.write("\"PL\": 64}")
        f.close()
        
