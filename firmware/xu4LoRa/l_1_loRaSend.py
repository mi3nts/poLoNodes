
# MQTT Client demo
# Continuously monitor two different MQTT topics for data,
# check if the received data matches two predefined 'commands'

import base64
from cgitb import strong
# import imp
# from this import d
import paho.mqtt.client as mqtt
import datetime 
from datetime import timedelta
import yaml
import collections
import json
import time 
import serial.tools.list_ports
from collections import OrderedDict
from glob import glob
from mintsXU4 import mintsDefinitions as mD
from mintsXU4 import mintsPoLo as mPL
from collections import OrderedDict
import struct
import numpy as np
import pynmea2
import shutil

#import SI1132
from mintsI2c.i2c_scd30 import SCD30
from mintsI2c.i2c_as7265x import AS7265X
import math
import sys
import time
import os
import smbus2



debug  = False 

bus     = smbus2.SMBus(0)
scd30   = SCD30(bus,debug)
as7265x = AS7265X(bus,debug)

loRaE5MiniPorts     = mD.loRaE5MiniPorts
canareePorts        = mD.canareePorts
gpsPorts            = mD.gpsPorts
appKey              = mD.appKey
macAddress          = mD.macAddress
jsonFolderName      = mD.dataFolderJson


def getLatitudeCords(latitudeStr,latitudeDirection):
    latitude = float(latitudeStr)
    latitudeCord      =  math.floor(latitude/100) +(latitude - 100*(math.floor(latitude/100)))/60
    if(latitudeDirection=="S"):
        latitudeCord = -1*latitudeCord
    return latitudeCord

def getLongitudeCords(longitudeStr,longitudeDirection):
    longitude = float(longitudeStr)
    longitudeCord      =  math.floor(longitude/100) +(longitude - 100*(math.floor(longitude/100)))/60
    if(longitudeDirection=="W"):
        longitudeCord = -1*longitudeCord
    return longitudeCord        

if __name__ == "__main__":
    
    print()
    print("============ MINTS POLO NODES ============")
    print()
    
    mPL.readingDeviceProperties(macAddress,loRaE5MiniPorts,canareePorts,gpsPorts)
    
    print("")
    
    e5MiniOnline,serE5Mini   = mPL.getPort(loRaE5MiniPorts,0,9600)
    canareeOnline,serCanaree = mPL.getPort(canareePorts,0,115200)
    gpsOnline,serGps         = mPL.getPort(gpsPorts,0,115200)

    # I2C Devices 
    scd30Online    = scd30.initiate(30)
    as7265xOnline  = as7265x.initiate()

    joined  = mPL.loRaE5MiniJoin(e5MiniOnline,serE5Mini)
    # joined = True    

    while joined:
        # Add a try catch 
        start_time = time.time()
        
        mPL.readSensorData(canareeOnline,serCanaree,"IPS7100CNR",serE5Mini)
        mPL.readSensorData(canareeOnline,serCanaree,"BME688CNR",serE5Mini)
        mPL.readSensorData(canareeOnline,serCanaree,"IPS7100CNR",serE5Mini)
        mPL.readSensorDataI2c(canareeOnline,scd30,"SCD30",serE5Mini)
        mPL.readSensorData(canareeOnline,serCanaree,"IPS7100CNR",serE5Mini)
        mPL.readSensorDataI2c(canareeOnline,as7265x,"AS7265X",serE5Mini)
        mPL.readSensorData(canareeOnline,serCanaree,"IPS7100CNR",serE5Mini)
        mPL.readSensorDataGPS(gpsOnline,serGps,"GPGGA",serE5Mini)
        mPL.readSensorData(canareeOnline,serCanaree,"IPS7100CNR",serE5Mini)
        mPL.readSensorDataGPS(gpsOnline,serGps,"GPRMC",serE5Mini)        
        
        jsonFiles = glob(jsonFolderName+ "/*.json", recursive = True)
        time.sleep(1)
        for idx, fileIn in enumerate(jsonFiles):
            if(idx>=0):
            	print("Too Many JSON files")
            	break;
            print("-======================================================================-")
            print("Looking up file: " + fileIn +" with index:" + str(idx)) 
            baseDateTime = fileIn.replace("_mintsAudio.json","").split('/')
            duration     = datetime.datetime.now() - datetime.datetime.strptime(\
                                baseDateTime[-1], '%Y_%m_%d_%H_%M_%S_%f')
            durSeconds = int(duration.total_seconds())
            
            if durSeconds < 65534:
                with open(fileIn, 'r') as f:
                    jsonData = json.load(f)
            
                sensorData = [durSeconds,jsonData['label'],jsonData['confidence']]
                mPL.readSensorDataBirdSong(sensorData,"MBCLR001",serE5Mini)
          	
            if os.path.isfile(fileIn):
                print("Deleting file: " +fileIn)
                os.remove(fileIn)
        time.sleep(1)
        
        
        
        
        
        
        
        