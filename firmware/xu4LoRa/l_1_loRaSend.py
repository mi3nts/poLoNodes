
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

loRaE5MiniPorts     = mD.loRaE5MiniPorts
canareePorts        = mD.canareePorts
gpsPorts            = mD.gpsPorts
appKey              = mD.appKey
macAddress          = mD.macAddress


if __name__ == "__main__":

    mPL.readingDeviceProperties(macAddress,loRaE5MiniPorts,canareePorts,gpsPorts)
    
    availE5Mini,serE5Mini   = mPL.getPort(loRaE5MiniPorts,0,9600)
    availCanaree,serCanaree = mPL.getPort(canareePorts,0,115200)

    joined, serE5Mini  = mPL.loRaE5MiniJoin(macAddress,loRaE5MiniPorts,canareePorts,gpsPorts)
    
    while joined:

        # Code Later
        # At this point we work on the canaree 
        # sensorData = readSerialLineStr(serGPS,2,"GGA")
        # print(sensorData)
        # sensorData = readSerialLineStr(serGPS,2,"RMC")
        # print(sensorData)

        sensorData = mPL.readSerialLine(serCanaree,2,44)
        # strOut = getMessegeStringHex(sensorData, "IPS7100CNR")
        # sendCommand(serE5Mini,'AT+PORT=17',2)
        # sendCommand(serE5Mini,'AT+MSGHEX='+str(strOut),5)


        sensorData = mPL.readSerialLine(serCanaree,2,44)
        # strOut = getMessegeStringHex(sensorData, "BME688CNR")
        # sendCommand(serE5Mini,'AT+PORT=25',2)
        # sendCommand(serE5Mini,'AT+MSGHEX='+str(strOut),5)



