
# MQTT Client demo
# Continuously monitor two different MQTT topics for data,
# check if the received data matches two predefined 'commands'
import base64
from cgitb import strong
import imp
from this import d
import paho.mqtt.client as mqtt
import datetime
import yaml
import collections
import json
import time 
import serial.tools.list_ports
from collections import OrderedDict

from mintsXU4 import mintsDefinitions as mD
from mintsXU4 import mintsPoLo as mPL
from collections import OrderedDict
import struct
import numpy as np


#import SI1132
from mintsI2c.i2c_scd30 import SCD30
from mintsI2c.i2c_as7265x import AS7265X

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


if __name__ == "__main__":

    mPL.readingDeviceProperties(macAddress,loRaE5MiniPorts,canareePorts,gpsPorts)
    
    availE5Mini,serE5Mini   = mPL.getPort(loRaE5MiniPorts,0,9600)
    
    availCanaree,serCanaree = mPL.getPort(canareePorts,0,115200)
    availGps,serGps         = mPL.getPort(gpsPorts,0,115200)

    # I2C Devices 
    scd30_valid    = scd30.initiate(30)
    as7265x_valid  = as7265x.initiate()


    joined  = mPL.loRaE5MiniJoin(availE5Mini,serE5Mini)
    
    while joined:

        # Code Later
        # At this point we work on the canaree 
        start_time = time.time()
        # Read GPS
        # Add Validity Port Check 
        sensorData = mPL.readSerialLineStr(serGps,2,"GGA")
        print(sensorData)
        sensorData = mPL.readSerialLineStr(serGps,2,"RMC")
        print(sensorData)

        # Read IPS7100
        # Add Canaree Check 
        sensorData = mPL.readSerialLine(serCanaree,2,44)
        print(sensorData)
        strOut = mPL.getMessegeStringHex(sensorData, "IPS7100CNR")
        mPL.sendCommand(serE5Mini,'AT+PORT=17',2)
        mPL.sendCommand(serE5Mini,'AT+MSGHEX='+str(strOut),5)

        # Read BME688
        # Add Canaree Check 
        sensorData = mPL.readSerialLine(serCanaree,2,44)
        print(sensorData)
        strOut = mPL.getMessegeStringHex(sensorData, "BME688CNR")
        mPL.sendCommand(serE5Mini,'AT+PORT=25',2)
        mPL.sendCommand(serE5Mini,'AT+MSGHEX='+str(strOut),5)

        # Read SCD30
        print("======== SCD30 ========")
        if scd30_valid:
            strOut  =  scd30.read()
            print(strOut)
        print("=======================")
        time.sleep(2.5)

        # Read AS7265X
        print("======= AS7265X =======")
        if as7265x_valid:
            strOut  = as7265x.read()
            print(strOut)            
        print("=======================")
        time.sleep(2.5)

        print("--- %s seconds ---" % (time.time() - start_time))