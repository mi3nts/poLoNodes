# MQTT Client demo
# Continuously monitor two different MQTT topics for data,
# check if the received data matches two predefined 'commands'
import base64
from cgitb import strong
from this import d
import time 
import serial.tools.list_ports

from mintsXU4 import mintsDefinitions as mD
from mintsXU4 import mintsLoRaSensing as mLS

from collections import OrderedDict
import struct
import numpy as np

loRaE5MiniPorts     = mD.loRaE5MiniPorts
canareePorts        = mD.canareePorts
gpsPorts            = mD.gpsPorts
appKey              = mD.appKey
macAddress          = mD.macAddress
fPortIDs            = mD.fPortIDs
receiveTransmit     = True

 


def deriveSensorStats(sensorID):
    for port in fPortIDs:
        if(port['sensor'] == sensorID):
            return port;
    return port;

def getPort(portsIn,indexIn,baudRateIn):
    availabilty  = len(portsIn)>0
    serPort = []
    if(availabilty):
        serPort = openSerial(portsIn[indexIn],baudRateIn)
    return availabilty,serPort;

def readingDeviceProperties(macAddress,loRaE5MiniPorts,canareePorts,gpsPorts):
    
    print("Mac Address: {0}".format(macAddress))
    print()
    print("LoRa E5 Mini Ports:")
    for dev in loRaE5MiniPorts:
        print("\t{0}".format(dev))
    
    print("Canaree Ports:")
    for dev in canareePorts:
        print("\t{0}".format(dev))
    
    print("GPS Ports:")
    for dev in gpsPorts:
        print("\t{0}".format(dev))

    return;

def loRaE5MiniJoin(availE5Mini,serE5Mini):
    print()
    if (not availE5Mini):
        print("E5 Mini Not Connected")
        quit()
         
    joined = False 
    # Read E5 Mini Credentials
    sendCommand(serE5Mini,'AT+RESET',2)
    sendCommand(serE5Mini,'AT+FDEFAULT',1)
    sendCommand(serE5Mini,'AT+VER',1)
    sendCommand(serE5Mini,'AT+FDEFAULT',1)
    sendCommand(serE5Mini,'AT+ID',1)
    sendCommand(serE5Mini,'AT+KEY=APPKEY, "'+appKey+'"',1)
    sendCommand(serE5Mini,'AT+MODE=LWOTAA',1)
    sendCommand(serE5Mini,'AT+DR=US915',1)
    sendCommand(serE5Mini,'AT+DR=dr2',1)
    sendCommand(serE5Mini,'AT+CH=NUM, 56-63',1)
    sendCommand(serE5Mini,'AT+POWER=20',1)
    # Changing to Power Mode Polo F Port

    # sendCommand(serE5Mini,'AT+PORT=4',2)
    
    # Check Join
    joined = joinNetwork(10,serE5Mini,10)

    if not joined:
        time.sleep(60)
        joined  = joinNetwork(10,serE5Mini,10)

    if not joined:
        print("No Network Found")
        quit()
    else:
        print()
        print("Network Found")
        print()
    sensorID = "PM"    
    
    sendCommandHex(serE5Mini,sensorID,[254],deriveSensorStats(sensorID))
    
    # sendCommandHex(serE5Mini,sensorID,sensorData,port)
    # messege    = hex(struct.unpack('<I', struct.pack('<I', 254))[0])
    # messege = messege.replace('0x','').zfill(2)
    # sendCommand(serE5Mini,'AT+MSGHEX='+str(messege),5)
    
    return joined ;


def openSerial(portIn,baudRate):
    ser = serial.Serial(
            port= portIn,\
            baudrate=baudRate,\
            parity  =serial.PARITY_NONE,\
            stopbits=serial.STOPBITS_ONE,\
            bytesize=serial.EIGHTBITS,\
            timeout=0)

    print(" ")
    print("Connected to: " + ser.portstr)
    # print(" ")
    return ser;

def sendCommand2(serIn,commandStrIn,timeOutIn):
    serIn.write(str.encode(commandStrIn+ '\n\r'))
    line = []
    lines = []
    startTime = time.time()
    while (time.time()-startTime)<timeOutIn:
        for c in serIn.read():
            line.append(chr(c))
            if chr(c) == '\n':
                dataString = (''.join(line)).replace("\n","").replace("\r","")
                lines.append(dataString)
                # print(dataString)
                line = []
                break
    return serIn,lines;


def sendCommand(serIn,commandStrIn,timeOutIn):
    serIn.write(str.encode(commandStrIn+ '\n\r'))
    line = []
    lines = []
    startTime = time.time()
    while (time.time()-startTime)<timeOutIn:
        for c in serIn.read():
            line.append(chr(c))
            if chr(c) == '\n':
                dataString = (''.join(line)).replace("\n","").replace("\r","")
                lines.append(dataString)
                # print(dataString)
                line = []
                break
    return lines;

        # except:
        #     print("Incomplete String Read")
        #     line = []
def readSerialLineStrAsIs(serIn,timeOutSensor,strExpected):
    line = []
    startTime = time.time()
    startFound = False
    while (time.time()-startTime)<timeOutSensor:   
        # try:
            for c in serIn.read():
                line.append(chr(c))
                # print((''.join(line)))

                if chr(c) == '\n':
                    if startFound == True:
                        dataString     = (''.join(line))
                        dataStringPost = dataString.replace('\r\n', '')
                        
                        if dataStringPost.find(strExpected) >0:
                            return dataStringPost;
                        else:
                            line = []
                    else:    
                        startFound = True
                        line = []




def readSerialLineStr(serIn,timeOutSensor,strExpected):
    line = []
    startTime = time.time()
    startFound = False
    while (time.time()-startTime)<timeOutSensor:   
        # try:
            for c in serIn.read():
                line.append(chr(c))
                # print((''.join(line)))

                if chr(c) == '\n':
                    if startFound == True:
                        dataString     = (''.join(line))
                        dataStringPost = dataString.replace('\r\n', '')
                        dataStringData =  dataStringPost.split(',')
                        
                        if dataStringPost.find(strExpected) >0:
                            return dataStringData;
                        else:
                            line = []
                    else:    
                        startFound = True
                        line = []

        # except:
        #     print("Incomplete String Read")
        #     line = []

def swapBytes(inputIn):
    return bytes([c for t in zip(inputIn[1::2], inputIn[::2]) for c in t])


def getMessegeStringHex(dataIn, sensorIn):
     if sensorIn == "SCD30":
        strOut  = \
            np.uint32(dataIn[0]).tobytes().hex().zfill(8)+ \
            np.uint32(dataIn[1]).tobytes().hex().zfill(8) + \
            np.uint32(dataIn[2]).tobytes().hex().zfill(8)
        return strOut;

     if sensorIn == "AS7265X":
        strOut  = \
            np.uint32(dataIn[0]).tobytes().hex().zfill(8)+ \
            np.uint32(dataIn[1]).tobytes().hex().zfill(8) + \
            np.uint32(dataIn[2]).tobytes().hex().zfill(8)+ \
            np.uint32(dataIn[3]).tobytes().hex().zfill(8) + \
            np.uint32(dataIn[4]).tobytes().hex().zfill(8)+ \
            np.uint32(dataIn[5]).tobytes().hex().zfill(8) + \
            np.uint32(dataIn[6]).tobytes().hex().zfill(8)+ \
            np.float32(dataIn[7]).tobytes().hex().zfill(8)+ \
            np.float32(dataIn[8]).tobytes().hex().zfill(8) + \
            np.float32(dataIn[9]).tobytes().hex().zfill(8)+ \
            np.float32(dataIn[10]).tobytes().hex().zfill(8) + \
            np.float32(dataIn[11]).tobytes().hex().zfill(8)+ \
            np.float32(dataIn[12]).tobytes().hex().zfill(8) + \
            np.float32(dataIn[13]).tobytes().hex().zfill(8)
        return strOut;

     if sensorIn == "IPS7100CNR":
        strOut  = \
            np.uint32(dataIn[1]).tobytes().hex().zfill(8)+ \
            np.uint32(dataIn[3]).tobytes().hex().zfill(8) + \
            np.uint32(dataIn[5]).tobytes().hex().zfill(8)+ \
            np.uint32(dataIn[7]).tobytes().hex().zfill(8) + \
            np.uint32(dataIn[9]).tobytes().hex().zfill(8)+ \
            np.uint32(dataIn[11]).tobytes().hex().zfill(8) + \
            np.uint32(dataIn[13]).tobytes().hex().zfill(8)+ \
            np.float32(dataIn[15]).tobytes().hex().zfill(8)+ \
            np.float32(dataIn[17]).tobytes().hex().zfill(8) + \
            np.float32(dataIn[19]).tobytes().hex().zfill(8)+ \
            np.float32(dataIn[21]).tobytes().hex().zfill(8) + \
            np.float32(dataIn[23]).tobytes().hex().zfill(8)+ \
            np.float32(dataIn[25]).tobytes().hex().zfill(8) + \
            np.float32(dataIn[27]).tobytes().hex().zfill(8)

        return strOut;

     if sensorIn == "BME688CNR":
        strOut  = \
            np.float32(dataIn[29]).tobytes().hex().zfill(8)+ \
            np.float32(dataIn[31]).tobytes().hex().zfill(8) + \
            np.float32(dataIn[33]).tobytes().hex().zfill(8)+ \
            np.float32(dataIn[35]).tobytes().hex().zfill(8) + \
            np.float32(dataIn[37]).tobytes().hex().zfill(8)+ \
            np.float32(dataIn[39]).tobytes().hex().zfill(8) + \
            np.float32(dataIn[41]).tobytes().hex().zfill(8)
        return strOut;

    
def joinNetwork(numberOfTries,ser,timeOutIn):
    for currentTry in range(numberOfTries):
        print("Joining Network Trial: " + str(currentTry))
        lines = sendCommand(ser,'AT+JOIN',timeOutIn)
        
        for line in lines:
            if line == '+JOIN: Network joined':
                return True;

    return False;

def readSerialLine(serIn,timeOutSensor,sizeExpected):
    line = []
    startTime = time.time()
    startFound = False
    while (time.time()-startTime)<timeOutSensor:   
        # try:
            for c in serIn.read():
                line.append(chr(c))
                # print((''.join(line)))
                if chr(c) == '\n':
                    if startFound == True:
                        dataString     = (''.join(line))
                        dataStringPost = dataString.replace('\r\n', '')
                        dataStringData =  dataStringPost.split(',')
                        print("Read Serial Line")
                        if sizeExpected == len(dataStringData):
                            print("Returning Data")
                            return dataStringData;
                        else:
                            line = []
                    else:    
                        startFound = True
                        line = []

def sendCommandHex(serPortE5,sensorID,sensorData,port):
    hexString = mLS.encodeDecode( sensorID,sensorData,receiveTransmit)
    sendCommand(serPortE5,'AT+PORT='+ str(port['portID']),2) 
    sendCommand(serPortE5,'AT+MSGHEX='+str(hexString ),5)    
  

def readSensorData(online,serPort,sensorID,serPortE5):
    print("====================================")  
    print("-----------" +sensorID+ "-----------" ) 
    if online:
        print(sensorID + " Online") 
        port = deriveSensorStats(sensorID)
        if port['portID']<255:
            sensorData = readSerialLine(serPort,2,port['numOfParametors'])
            print(sensorData)
            sendCommandHex(serPortE5,sensorID,sensorData,port)
            return;
    else:
        print(sensorID + " Offline")       
        return;
        
def readSensorDataI2c(online,i2cObject,sensorID,serPortE5):
    print("====================================")  
    print("-----------" +sensorID+ "-----------" ) 
    if online:
        print(" ------------------------------ ")  
        print(sensorID + " Online")  
        port = deriveSensorStats(sensorID)
        if port['portID']<255:
            print("Reading I2C Data")
            sensorData  =  i2cObject.read()
            print(sensorData)
            sendCommandHex(serPortE5,sensorID,sensorData,port)  
            return;
    else:
        print(sensorID + " Offline")       
        return;

        