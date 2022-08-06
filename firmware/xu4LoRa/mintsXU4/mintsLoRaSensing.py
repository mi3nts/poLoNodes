
import serial
import datetime
import os
import csv
#import deepdish as dd
# from mintsXU4 import mintsLatest as mL
from mintsXU4 import mintsDefinitions as mD
# from mintsXU4 import mintsSensorReader as mSR
from getmac import get_mac_address
import time
import serial
import pynmea2
from collections import OrderedDict
import math
import base64
import json
import struct
import numpy as np

macAddress     = mD.macAddress
dataFolder     = mD.dataFolder
fPortIDs        = mD.fPortIDs

mqttOn         = mD.mqttOn
decoder        = json.JSONDecoder(object_pairs_hook=OrderedDict)


def loRaSummaryReceive(message,fPortIDs):
    nodeID = message.topic.split('/')[5]
    sensorPackage       =  decoder.decode(message.payload.decode("utf-8","ignore"))
    rxInfo              =  sensorPackage['rxInfo'][0]
    txInfo              =  sensorPackage['txInfo']
    loRaModulationInfo  =  txInfo['loRaModulationInfo']
    sensorID            = fPortIDs[getPortIndex(sensorPackage['fPort'],fPortIDs)]['sensor']
    dateTime            = datetime.datetime.fromisoformat(sensorPackage['publishedAt'][0:26])
    base16Data          = base64.b64decode(sensorPackage['data'].encode()).hex()
    gatewayID           = base64.b64decode(rxInfo['gatewayID']).hex()
    framePort           = sensorPackage['fPort']
    sensorDictionary =  OrderedDict([
            ("dateTime"        , str(dateTime)),
            ("nodeID"          , nodeID),
            ("sensorID"        , sensorID),
            ("gatewayID"       , gatewayID),
            ("rssi"            , rxInfo["rssi"]),
            ("loRaSNR"         , rxInfo["loRaSNR"]),
            ("channel"         , rxInfo["channel"] ),
            ("rfChain"         , rxInfo["rfChain"] ),
            ("frequency"       , txInfo["frequency"]),
            ("bandwidth"       , loRaModulationInfo["bandwidth"]),
            ("spreadingFactor" , loRaModulationInfo["spreadingFactor"] ),
            ("codeRate"        , loRaModulationInfo["codeRate"] ),
            ("dataRate"        , sensorPackage['dr']),
            ("frameCounters"   , sensorPackage['fCnt']),
            ("framePort"       , framePort),
            ("base64Data"      , sensorPackage['data']),
            ("base16Data"      , base16Data),
            ("devAddr"         , sensorPackage['devAddr']),
            ("deviceAddDecoded", base64.b64decode(sensorPackage['devAddr'].encode()).hex())
        ])
    return dateTime,gatewayID,nodeID,sensorID,framePort,base16Data;


def getPortIndex(portIDIn,fPortIDs):
    indexOut = 0
    for portID in fPortIDs:
        if (portIDIn == portID['portID']):
            return indexOut; 
        indexOut = indexOut +1
    return -1;


def encodeDecode(sensorID,sensorData,transmitReceive):
    # print("Encode Decode")
    if sensorID == "IPS7100CNR":
        return sensingIPS7100CNR(sensorData,transmitReceive);
    if sensorID == "BME688CNR":
        return sensingBME688CNR(sensorData,transmitReceive); 
    if sensorID == "SCD30":
        return sensingSCD30(sensorData,transmitReceive);           
    if sensorID == "AS7265X":
        return sensingAS7265X(sensorData,transmitReceive);   
    if sensorID == "PM":
        return sensingPM(sensorData,transmitReceive);   
    if sensorID == "PMPoLo":
        return sensingPM(sensorData,transmitReceive); 
    if sensorID == "MacAD":
        return sensingMacAD(sensorData,transmitReceive);      
    if sensorID == "GPGGA":
        return sensingGPGGA(sensorData,transmitReceive);         
    if sensorID == "GPRMC":
        return sensingGPRMC(sensorData,transmitReceive);   
    return " "   
        
    # For transmitting data, transmitRecieve is True

def sensingPM(dataIn,transmitReceive):
    print("Reading Power Mode")	
    if (transmitReceive): 
        strOut  = \
            np.ubyte(dataIn[0]).tobytes().hex().zfill(2)
        return strOut;  
    else:
        dateTime = datetime.datetime.now()
        sensorDictionary =  OrderedDict([
                ("dateTime"      ,str(dateTime)),
                ("powerMode",struct.unpack('<B',bytes.fromhex(dataIn[0:8]))[0])
        ])
        return sensorDictionary;

def sensingPMPoLo(dataIn,transmitReceive):
    print("Reading Power Mode")	
    if (transmitReceive): 
        strOut  = \
            np.ubyte(dataIn[0]).tobytes().hex().zfill(2)
        return strOut;  
    else:
        dateTime = datetime.datetime.now()
        sensorDictionary =  OrderedDict([
                ("dateTime"      ,str(dateTime)),
                ("powerMode",struct.unpack('<B',bytes.fromhex(dataIn[0:2]))[0])
        ])
        return sensorDictionary;

def sensingMacAD(dataIn,transmitReceive):
    print("Reading Mac Address")	
    if (transmitReceive): 
        strOut  = \
            dataIn[0].zfill(12)
        return strOut;  
    else:
        dateTime = datetime.datetime.now()
        sensorDictionary =  OrderedDict([
                ("dateTime"      ,str(dateTime)),
                ("macAddress" ,dataIn),
        ])
        return sensorDictionary;

        
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


def sensingGPGGA(dataIn,transmitReceive):

    if (transmitReceive): 
        dataIn = pynmea2.parse(dataIn)
        if (dataIn.gps_qual>0):
            timeStamp = str(dataIn.timestamp).split(":")
            print("GPGGA Read")	
            strOut  = \
                np.ubyte(timeStamp[0]).tobytes().hex().zfill(2)+ \
                np.ubyte(timeStamp[1]).tobytes().hex().zfill(2)+ \
                np.ubyte(timeStamp[2]).tobytes().hex().zfill(2)+ \
                np.double(getLatitudeCords(dataIn.lat,dataIn.lat_dir)).tobytes().hex().zfill(16)+ \
                np.double(getLongitudeCords(dataIn.lon,dataIn.lon_dir)).tobytes().hex().zfill(16) + \
                np.ubyte(dataIn.gps_qual).tobytes().hex().zfill(2)+ \
                np.ubyte(dataIn.num_sats).tobytes().hex().zfill(2)+ \
                np.float32(dataIn.horizontal_dil).tobytes().hex().zfill(8) +\
                np.float32(dataIn.altitude).tobytes().hex().zfill(8) +\
                np.float32(dataIn.geo_sep).tobytes().hex().zfill(8) ;
            return strOut;  
        else:
            print("GPGGA Data Not Read: No GPS Signal")	

    else:
        dateTime = datetime.datetime.now()
        sensorDictionary =  OrderedDict([
                ("dateTime"            ,str(dateTime)),
        		("hour"                ,struct.unpack('<B',bytes.fromhex(dataIn[0:2]))[0]),
                ("minute"              ,struct.unpack('<B',bytes.fromhex(dataIn[2:4]))[0]),
                ("second"              ,struct.unpack('<B',bytes.fromhex(dataIn[4:6]))[0]),
            	("latitudeCoordinate"  ,struct.unpack('<d',bytes.fromhex(dataIn[6:22]))[0]),
                ("longitudeCoordinate" ,struct.unpack('<d',bytes.fromhex(dataIn[22:38]))[0]),
	            ("gpsQuality"          ,struct.unpack('<B',bytes.fromhex(dataIn[38:40]))[0]),
                ("numberOfSatellites"  ,struct.unpack('<B',bytes.fromhex(dataIn[40:42]))[0]),
                ("HorizontalDilution"  ,struct.unpack('<f',bytes.fromhex(dataIn[42:50]))[0]),
            	("altitude"            ,struct.unpack('<f',bytes.fromhex(dataIn[50:58]))[0]),
        		("undulation"          ,struct.unpack('<f',bytes.fromhex(dataIn[58:66]))[0]),
        ])
        return sensorDictionary;

def sensingGPRMC(dataIn,transmitReceive):

    if (transmitReceive): 
        dataIn = pynmea2.parse(dataIn)
        if (dataIn.status=='A'):
            timeStamp = str(dataIn.timestamp).split(":")
            dateStamp = str(dataIn.datestamp).split("-")
            print("GPRMC Read")	
            strOut  = \
                np.uint16(dateStamp[0]).tobytes().hex().zfill(4)+ \
                np.ubyte(dateStamp[1]).tobytes().hex().zfill(2)+ \
                np.ubyte(dateStamp[2]).tobytes().hex().zfill(2)+ \
                np.ubyte(timeStamp[0]).tobytes().hex().zfill(2)+ \
                np.ubyte(timeStamp[1]).tobytes().hex().zfill(2)+ \
                np.ubyte(timeStamp[2]).tobytes().hex().zfill(2)+ \
                np.double(getLatitudeCords(dataIn.lat,dataIn.lat_dir)).tobytes().hex().zfill(16)+ \
                np.double(getLongitudeCords(dataIn.lon,dataIn.lon_dir)).tobytes().hex().zfill(16) + \
                np.float32(dataIn.spd_over_grnd).tobytes().hex().zfill(8) ;
            return strOut;  
        else:
            print("GPRMC Data Not Read: No GPS Signal")	

    else:
        dateTime = datetime.datetime.now()
        sensorDictionary =  OrderedDict([
                ("dateTime"            ,str(dateTime)),
         		("year"                ,struct.unpack('<H',bytes.fromhex(dataIn[0:4]))[0]),
                ("month"               ,struct.unpack('<B',bytes.fromhex(dataIn[4:6]))[0]),
                ("day"                 ,struct.unpack('<B',bytes.fromhex(dataIn[6:8]))[0]),               
        		("hour"                ,struct.unpack('<B',bytes.fromhex(dataIn[8:10]))[0]),
                ("minute"              ,struct.unpack('<B',bytes.fromhex(dataIn[10:12]))[0]),
                ("second"              ,struct.unpack('<B',bytes.fromhex(dataIn[12:14]))[0]),
            	("latitudeCoordinate"  ,struct.unpack('<d',bytes.fromhex(dataIn[14:30]))[0]),
                ("longitudeCoordinate" ,struct.unpack('<d',bytes.fromhex(dataIn[30:46]))[0]),
        		("speedOverGround"     ,struct.unpack('<f',bytes.fromhex(dataIn[46:54]))[0]),
        ])
        return sensorDictionary;


def sensingAS7265X(dataIn,transmitReceive):

    if (transmitReceive): 
        print("AS7265X Read")	
        strOut  = \
            np.float32(dataIn[0]).tobytes().hex().zfill(8)+ \
            np.float32(dataIn[1]).tobytes().hex().zfill(8) + \
            np.float32(dataIn[2]).tobytes().hex().zfill(8)+ \
            np.float32(dataIn[3]).tobytes().hex().zfill(8) + \
            np.float32(dataIn[4]).tobytes().hex().zfill(8)+ \
            np.float32(dataIn[5]).tobytes().hex().zfill(8) + \
            np.float32(dataIn[6]).tobytes().hex().zfill(8)+ \
            np.float32(dataIn[7]).tobytes().hex().zfill(8) + \
            np.float32(dataIn[8]).tobytes().hex().zfill(8)+ \
            np.float32(dataIn[9]).tobytes().hex().zfill(8) + \
            np.float32(dataIn[10]).tobytes().hex().zfill(8)+ \
            np.float32(dataIn[11]).tobytes().hex().zfill(8) + \
            np.float32(dataIn[12]).tobytes().hex().zfill(8)+ \
            np.float32(dataIn[13]).tobytes().hex().zfill(8) + \
            np.float32(dataIn[14]).tobytes().hex().zfill(8)+ \
            np.float32(dataIn[15]).tobytes().hex().zfill(8) + \
            np.float32(dataIn[16]).tobytes().hex().zfill(8)+ \
            np.float32(dataIn[17]).tobytes().hex().zfill(8) ;
            
   
        return strOut;  
    else:
        dateTime = datetime.datetime.now()
        sensorDictionary =  OrderedDict([
                ("dateTime"      ,str(dateTime)),
        		("channelA410nm" ,struct.unpack('<f',bytes.fromhex(dataIn[0:8]))[0]),
            	("channelB435nm" ,struct.unpack('<f',bytes.fromhex(dataIn[8:16]))[0]),
        		("channelC460nm" ,struct.unpack('<f',bytes.fromhex(dataIn[16:24]))[0]),
            	("channelD485nm" ,struct.unpack('<f',bytes.fromhex(dataIn[24:32]))[0]),                
        		("channelE510nm" ,struct.unpack('<f',bytes.fromhex(dataIn[32:40]))[0]),
            	("channelF535nm" ,struct.unpack('<f',bytes.fromhex(dataIn[40:48]))[0]),
        		("channelG560nm" ,struct.unpack('<f',bytes.fromhex(dataIn[48:56]))[0]),
            	("channelH585nm" ,struct.unpack('<f',bytes.fromhex(dataIn[56:64]))[0]),                
        		("channelR610nm" ,struct.unpack('<f',bytes.fromhex(dataIn[64:72]))[0]),
            	("channelI645nm" ,struct.unpack('<f',bytes.fromhex(dataIn[72:80]))[0]),
        		("channelS680nm" ,struct.unpack('<f',bytes.fromhex(dataIn[80:88]))[0]),
            	("channelJ705nm" ,struct.unpack('<f',bytes.fromhex(dataIn[88:96]))[0]),                
        		("channelT730nm" ,struct.unpack('<f',bytes.fromhex(dataIn[96:104]))[0]),
            	("channelU760nm" ,struct.unpack('<f',bytes.fromhex(dataIn[104:112]))[0]),
        		("channelV810nm" ,struct.unpack('<f',bytes.fromhex(dataIn[112:120]))[0]),
            	("channelW860nm" ,struct.unpack('<f',bytes.fromhex(dataIn[120:128]))[0]),                
        		("channelK900nm" ,struct.unpack('<f',bytes.fromhex(dataIn[128:136]))[0]),
            	("channelL940nm" ,struct.unpack('<f',bytes.fromhex(dataIn[136:144]))[0]),
        ])
        return sensorDictionary;

def sensingSCD30(dataIn,transmitReceive):

    if (transmitReceive): 
        print("SCD30 Read")	
        strOut  = \
            np.float32(dataIn[0]).tobytes().hex().zfill(8)+ \
            np.float32(dataIn[1]).tobytes().hex().zfill(8) + \
            np.float32(dataIn[2]).tobytes().hex().zfill(8)
        return strOut;  
    else:
        dateTime = datetime.datetime.now()
        sensorDictionary =  OrderedDict([
                ("dateTime"     ,str(dateTime)),
        		("co2"          ,struct.unpack('<f',bytes.fromhex(dataIn[0:8]))[0]),
            	("temperature"  ,struct.unpack('<f',bytes.fromhex(dataIn[8:16]))[0]),
                ("humidity"     ,struct.unpack('<f',bytes.fromhex(dataIn[16:24]))[0]),
        ])
        return sensorDictionary;

def sensingBME688CNR(dataIn,transmitReceive):

    if (transmitReceive): 
        print("BME688CNR Read")	
        strOut  = \
            np.float32(dataIn[29]).tobytes().hex().zfill(8)+ \
            np.float32(dataIn[31]).tobytes().hex().zfill(8) + \
            np.float32(dataIn[33]).tobytes().hex().zfill(8)+ \
            np.float32(dataIn[35]).tobytes().hex().zfill(8) + \
            np.float32(dataIn[37]).tobytes().hex().zfill(8)+ \
            np.float32(dataIn[39]).tobytes().hex().zfill(8) + \
            np.float32(dataIn[41]).tobytes().hex().zfill(8)
        return strOut;  
    else:
        dateTime = datetime.datetime.now()
        sensorDictionary =  OrderedDict([
                ("dateTime"    , str(dateTime)), 
        		("temperature" ,struct.unpack('<f',bytes.fromhex(dataIn[0:8]))[0]),
            	("humidity"    ,struct.unpack('<f',bytes.fromhex(dataIn[8:16]))[0]),
                ("pressure"    ,struct.unpack('<f',bytes.fromhex(dataIn[16:24]))[0]),
                ("vocAqi"      ,struct.unpack('<f',bytes.fromhex(dataIn[24:32]))[0]),
            	("bvocEq"      ,struct.unpack('<f',bytes.fromhex(dataIn[32:40]))[0]),
        		("gasEst"      ,struct.unpack('<f',bytes.fromhex(dataIn[40:48]))[0]), 
            	("co2Eq"       ,struct.unpack('<f',bytes.fromhex(dataIn[48:56]))[0]),
        ])
        return sensorDictionary;

    
def sensingIPS7100CNR(dataIn,transmitReceive):

    if (transmitReceive):  
        print("IPS7100CNR Read")	
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
    else:
        dateTime = datetime.datetime.now()
        sensorDictionary =  OrderedDict([
                ("dateTime" , str(dateTime)), 
        		("pc0_1"  ,struct.unpack('<L',bytes.fromhex(dataIn[0:8]))[0]),
            	("pc0_3"  ,struct.unpack('<L',bytes.fromhex(dataIn[8:16]))[0]),
                ("pc0_5"  ,struct.unpack('<L',bytes.fromhex(dataIn[16:24]))[0]),
                ("pc1_0"  ,struct.unpack('<L',bytes.fromhex(dataIn[24:32]))[0]),
            	("pc2_5"  ,struct.unpack('<L',bytes.fromhex(dataIn[32:40]))[0]),
        		("pc5_0"  ,struct.unpack('<L',bytes.fromhex(dataIn[40:48]))[0]), 
            	("pc10_0" ,struct.unpack('<L',bytes.fromhex(dataIn[48:56]))[0]),
        		("pm0_1"  ,struct.unpack('<f',bytes.fromhex(dataIn[56:64]))[0]), 
            	("pm0_3"  ,struct.unpack('<f',bytes.fromhex(dataIn[64:72]))[0]),
                ("pm0_5"  ,struct.unpack('<f',bytes.fromhex(dataIn[72:80]))[0]),
                ("pm1_0"  ,struct.unpack('<f',bytes.fromhex(dataIn[80:88]))[0]),
            	("pm2_5"  ,struct.unpack('<f',bytes.fromhex(dataIn[88:96]))[0]),
        		("pm5_0"  ,struct.unpack('<f',bytes.fromhex(dataIn[96:104]))[0]), 
            	("pm10_0" ,struct.unpack('<f',bytes.fromhex(dataIn[104:112]))[0])
        ])
        return sensorDictionary;

def directoryCheck(outputPath):
    exists = os.path.isfile(outputPath)
    directoryIn = os.path.dirname(outputPath)
    if not os.path.exists(directoryIn):
        print("Creating a Directory @: " +directoryIn)
        os.makedirs(directoryIn)
    return exists


# def sensorReceiveLoRa(dateTime,nodeID,sensorID,framePort,base16Data):
#     sensorDictionary =  OrderedDict([
#                 ("dateTime" , str(dateTime))])
#     if(sensorID=="IPS7100"):
#         sensorDictionary = IPS7100LoRaWrite(dateTime,nodeID,sensorID,framePort,base16Data)
#     if(sensorID=="IPS7100CNR"):
#         sensorDictionary = IPS7100CNRLoRaWrite(dateTime,nodeID,sensorID,framePort,base16Data)        
#     if(sensorID=="BME688CNR"):
#         sensorDictionary =BME688CNRLoRaWrite(dateTime,nodeID,sensorID,framePort,base16Data)       
#     return sensorDictionary;


# def IPS7100CNRLoRaWrite(dateTime,nodeID,sensorID,framePort,base16Data):
#     if(framePort == 17 and len(base16Data) ==112) :
#         sensorDictionary =  OrderedDict([
#                 ("dateTime" , str(dateTime)), 
#         		("pc0_1"  ,struct.unpack('<L',bytes.fromhex(base16Data[0:8]))[0]),
#             	("pc0_3"  ,struct.unpack('<L',bytes.fromhex(base16Data[8:16]))[0]),
#                 ("pc0_5"  ,struct.unpack('<L',bytes.fromhex(base16Data[16:24]))[0]),
#                 ("pc1_0"  ,struct.unpack('<L',bytes.fromhex(base16Data[24:32]))[0]),
#             	("pc2_5"  ,struct.unpack('<L',bytes.fromhex(base16Data[32:40]))[0]),
#         		("pc5_0"  ,struct.unpack('<L',bytes.fromhex(base16Data[40:48]))[0]), 
#             	("pc10_0" ,struct.unpack('<L',bytes.fromhex(base16Data[48:56]))[0]),
#         		("pm0_1"  ,struct.unpack('<f',bytes.fromhex(base16Data[56:64]))[0]), 
#             	("pm0_3"  ,struct.unpack('<f',bytes.fromhex(base16Data[64:72]))[0]),
#                 ("pm0_5"  ,struct.unpack('<f',bytes.fromhex(base16Data[72:80]))[0]),
#                 ("pm1_0"  ,struct.unpack('<f',bytes.fromhex(base16Data[80:88]))[0]),
#             	("pm2_5"  ,struct.unpack('<f',bytes.fromhex(base16Data[88:96]))[0]),
#         		("pm5_0"  ,struct.unpack('<f',bytes.fromhex(base16Data[96:104]))[0]), 
#             	("pm10_0" ,struct.unpack('<f',bytes.fromhex(base16Data[104:112]))[0])
#         ])
#     print(sensorDictionary)        
#     # loRaWriteFinisher(nodeID,sensorID,dateTime,sensorDictionary)
#     return sensorDictionary;


# def IPS7100LoRaWrite(dateTime,nodeID,sensorID,framePort,base16Data):
#     if(framePort == 15 and len(base16Data) ==112) :
#         sensorDictionary =  OrderedDict([
#                 ("dateTime" , str(dateTime)), 
#         		("pc0_1"  ,struct.unpack('<L',bytes.fromhex(base16Data[0:8]))[0]),
#             	("pc0_3"  ,struct.unpack('<L',bytes.fromhex(base16Data[8:16]))[0]),
#                 ("pc0_5"  ,struct.unpack('<L',bytes.fromhex(base16Data[16:24]))[0]),
#                 ("pc1_0"  ,struct.unpack('<L',bytes.fromhex(base16Data[24:32]))[0]),
#             	("pc2_5"  ,struct.unpack('<L',bytes.fromhex(base16Data[32:40]))[0]),
#         		("pc5_0"  ,struct.unpack('<L',bytes.fromhex(base16Data[40:48]))[0]), 
#             	("pc10_0" ,struct.unpack('<L',bytes.fromhex(base16Data[48:56]))[0]),
#         		("pm0_1"  ,struct.unpack('<f',bytes.fromhex(base16Data[56:64]))[0]), 
#             	("pm0_3"  ,struct.unpack('<f',bytes.fromhex(base16Data[64:72]))[0]),
#                 ("pm0_5"  ,struct.unpack('<f',bytes.fromhex(base16Data[72:80]))[0]),
#                 ("pm1_0"  ,struct.unpack('<f',bytes.fromhex(base16Data[80:88]))[0]),
#             	("pm2_5"  ,struct.unpack('<f',bytes.fromhex(base16Data[88:96]))[0]),
#         		("pm5_0"  ,struct.unpack('<f',bytes.fromhex(base16Data[96:104]))[0]), 
#             	("pm10_0" ,struct.unpack('<f',bytes.fromhex(base16Data[104:112]))[0])
#         ])
#     print(sensorDictionary)        
#     # loRaWriteFinisher(nodeID,sensorID,dateTime,sensorDictionary)
#     return sensorDictionary;

# def BME688CNRLoRaWrite(dateTime,nodeID,sensorID,framePort,base16Data):
#     if(framePort == 25 and len(base16Data) ==56) :
#         sensorDictionary =  OrderedDict([
#                 ("dateTime"    , str(dateTime)), 
#         		("temperature" ,struct.unpack('<f',bytes.fromhex(base16Data[0:8]))[0]),
#             	("humidity"    ,struct.unpack('<f',bytes.fromhex(base16Data[8:16]))[0]),
#                 ("pressure"    ,struct.unpack('<f',bytes.fromhex(base16Data[16:24]))[0]),
#                 ("vocAqi"      ,struct.unpack('<f',bytes.fromhex(base16Data[24:32]))[0]),
#             	("bvocEq"      ,struct.unpack('<f',bytes.fromhex(base16Data[32:40]))[0]),
#         		("gasEst"      ,struct.unpack('<f',bytes.fromhex(base16Data[40:48]))[0]), 
#             	("co2Eq"       ,struct.unpack('<f',bytes.fromhex(base16Data[48:56]))[0]),
#         ])
#     print(sensorDictionary)        
#     # loRaWriteFinisher(nodeID,sensorID,dateTime,sensorDictionary)
#     return sensorDictionary;


# def sensorSendLoRa(dateTime,nodeID,sensorID,framePort,base16Data):
#     if(sensorID=="IPS7100"):
#         IPS7100LoRaWrite(dateTime,nodeID,sensorID,framePort,base16Data)
#     if(sensorID=="BME280"):
#         BME280LoRaWrite(dateTime,nodeID,sensorID,framePort,base16Data)        
#     if(sensorID=="SCD30"):
#         SCD30LoRaWrite(dateTime,nodeID,sensorID,framePort,base16Data) 
#     if(sensorID=="INA219Duo"):
#         INA219DuoLoRaWrite(dateTime,nodeID,sensorID,framePort,base16Data) 
#     if(sensorID=="MGS001"):
#         MGS001LoRaWrite(dateTime,nodeID,sensorID,framePort,base16Data) 
#     if(sensorID=="PM"):
#         PMLoRaWrite(dateTime,nodeID,sensorID,framePort,base16Data) 
#     if(sensorID=="GPGGALR"):
#         GPGGALRLoRaWrite(dateTime,nodeID,sensorID,framePort,base16Data) 


        









# def BME280LoRaWrite(dateTime,nodeID,sensorID,framePort,base16Data):
#     if(framePort == 21 and len(base16Data) ==24):
#         sensorDictionary =  OrderedDict([
#                 ("dateTime"    ,str(dateTime)), 
#         		("Temperature" ,struct.unpack('<f',bytes.fromhex(base16Data[0:8]))[0]),
#             	("Pressure"    ,struct.unpack('<f',bytes.fromhex(base16Data[8:16]))[0]),
#                 ("Humidity"    ,struct.unpack('<f',bytes.fromhex(base16Data[16:24]))[0]),
#           ])
#     print(sensorDictionary)        
#     loRaWriteFinisher(nodeID,sensorID,dateTime,sensorDictionary)
#     return sensorDictionary;

# def SCD30LoRaWrite(dateTime,nodeID,sensorID,framePort,base16Data):
#     if(framePort == 33 and len(base16Data) ==24):
#         sensorDictionary =  OrderedDict([
#                 ("dateTime"    ,str(dateTime)), 
#         		("CO2"         ,struct.unpack('<f',bytes.fromhex(base16Data[0:8]))[0]),
#             	("Temperature" ,struct.unpack('<f',bytes.fromhex(base16Data[8:16]))[0]),
#                 ("Humidity"    ,struct.unpack('<f',bytes.fromhex(base16Data[16:24]))[0]),
#           ])
#     print(sensorDictionary)        
#     loRaWriteFinisher(nodeID,sensorID,dateTime,sensorDictionary)
#     return sensorDictionary;
# def INA219DuoLoRaWrite(dateTime,nodeID,sensorID,framePort,base16Data):
#     if(framePort == 3 and len(base16Data) ==64):
#         sensorDictionary =  OrderedDict([
#                 ("dateTime"    ,str(dateTime)), 
#         		("shuntVoltageBattery" ,struct.unpack('<f',bytes.fromhex(base16Data[0:8]))[0]),
#             	("busVoltageBattery"   ,struct.unpack('<f',bytes.fromhex(base16Data[8:16]))[0]),
#                 ("currentBattery"      ,struct.unpack('<f',bytes.fromhex(base16Data[16:24]))[0]),
#                 ("powerBattery"        ,struct.unpack('<f',bytes.fromhex(base16Data[24:32]))[0]),
# 	            ("shuntVoltageSolar"   ,struct.unpack('<f',bytes.fromhex(base16Data[32:40]))[0]),
#             	("busVoltageSolar"     ,struct.unpack('<f',bytes.fromhex(base16Data[40:48]))[0]),
#                 ("currentSolar"        ,struct.unpack('<f',bytes.fromhex(base16Data[48:56]))[0]),
#                 ("powerSolar"          ,struct.unpack('<f',bytes.fromhex(base16Data[56:64]))[0]),
#           ])
#     print(sensorDictionary)        
#     loRaWriteFinisher(nodeID,sensorID,dateTime,sensorDictionary)
#     return sensorDictionary;
# def MGS001LoRaWrite(dateTime,nodeID,sensorID,framePort,base16Data):
#     if(framePort == 31 and len(base16Data) ==64):
#         sensorDictionary =  OrderedDict([
#                 ("dateTime" ,str(dateTime)), 
#         		("C2H5OH"   ,struct.unpack('<f',bytes.fromhex(base16Data[0:8]))[0]),
#             	("C3H8"     ,struct.unpack('<f',bytes.fromhex(base16Data[8:16]))[0]),
#                 ("C4H10"    ,struct.unpack('<f',bytes.fromhex(base16Data[16:24]))[0]),
#                 ("CH4"      ,struct.unpack('<f',bytes.fromhex(base16Data[24:32]))[0]),
# 	            ("CO"       ,struct.unpack('<f',bytes.fromhex(base16Data[32:40]))[0]),
#             	("H2"       ,struct.unpack('<f',bytes.fromhex(base16Data[40:48]))[0]),
#                 ("NH3"      ,struct.unpack('<f',bytes.fromhex(base16Data[48:56]))[0]),
#                 ("NO2"      ,struct.unpack('<f',bytes.fromhex(base16Data[56:64]))[0]),
#           ])
#     print(sensorDictionary)        
#     loRaWriteFinisher(nodeID,sensorID,dateTime,sensorDictionary)
#     return sensorDictionary;

# def GPGGALRLoRaWrite(dateTime,nodeID,sensorID,framePort,base16Data):
#     if(framePort == 5 and len(base16Data) ==110):
#         sensorDictionary =  OrderedDict([
#                 ("dateTime"   ,str(dateTime)), 
#         		("Latitude"   ,struct.unpack('<d',bytes.fromhex(base16Data[0:16]))[0]),
#             	("Longitude"  ,struct.unpack('<d',bytes.fromhex(base16Data[16:32]))[0]),
#                 ("Speed"      ,struct.unpack('<d',bytes.fromhex(base16Data[32:48]))[0]),
#                 ("Altitude"   ,struct.unpack('<d',bytes.fromhex(base16Data[48:64]))[0]),
# 	            ("Course"     ,struct.unpack('<d',bytes.fromhex(base16Data[64:80]))[0]),
#             	("HDOP"       ,struct.unpack('<d',bytes.fromhex(base16Data[80:96]))[0]),# 42 bytes
#                 ("Year"       ,struct.unpack('<H',bytes.fromhex(base16Data[96:100]))[0]),# 2 bytes
#                 ("Month"      ,struct.unpack('<b',bytes.fromhex(base16Data[100:102]))[0]),
#                 ("Day"        ,struct.unpack('<b',bytes.fromhex(base16Data[102:104]))[0]),
#                 ("Hour"       ,struct.unpack('<b',bytes.fromhex(base16Data[104:106]))[0]),
#                 ("Minute"     ,struct.unpack('<b',bytes.fromhex(base16Data[106:108]))[0]),
#                 ("Second"     ,struct.unpack('<b',bytes.fromhex(base16Data[108:110]))[0]), #5 bytes 
#           ])
#     print(sensorDictionary)        
#     loRaWriteFinisher(nodeID,sensorID,dateTime,sensorDictionary)
#     return sensorDictionary;


# def PMLoRaWrite(dateTime,nodeID,sensorID,framePort,base16Data):
    
#     if(framePort == 2 and len(base16Data) ==2):
#         sensorDictionary =  OrderedDict([
#                     ("dateTime" ,str(dateTime)), 
#                     ("powerMode",int(base16Data, 16)),
#             ])
#         print(sensorDictionary)        
#         loRaWriteFinisher(nodeID,sensorID,dateTime,sensorDictionary)
#         return sensorDictionary;   

#     if(framePort == 2 and len(base16Data) ==4):
#         sensorDictionary =  OrderedDict([
#                     ("dateTime" ,str(dateTime)), 
#                     ("powerMode",struct.unpack('<b',bytes.fromhex(base16Data[0:2]))[0]),
#             ])
#         print(sensorDictionary)        
#         loRaWriteFinisher(nodeID,sensorID,dateTime,sensorDictionary)
#         return sensorDictionary;       
    

# def loRaWriteFinisher(nodeID,sensorID,dateTime,sensorDictionary):
#     writePath = mSR.getWritePathMQTT(nodeID,sensorID,dateTime)
#     exists    = mSR.directoryCheck(writePath)
#     print(writePath)	
#     mSR.writeCSV2(writePath,sensorDictionary,exists)
#     mL.writeJSONLatestMQTT(sensorDictionary,nodeID,sensorID)
#     return;

# def loRaSummaryWrite(message,portIDs):
#     nodeID = message.topic.split('/')[5]
#     sensorPackage       =  decoder.decode(message.payload.decode("utf-8","ignore"))
#     rxInfo              =  sensorPackage['rxInfo'][0]
#     txInfo              =  sensorPackage['txInfo']
#     loRaModulationInfo  =  txInfo['loRaModulationInfo']
#     sensorID            = portIDs[getPortIndex(sensorPackage['fPort'],portIDs)]['sensor']
#     dateTime            = datetime.datetime.fromisoformat(sensorPackage['publishedAt'][0:26])
#     base16Data          = base64.b64decode(sensorPackage['data'].encode()).hex()
#     gatewayID           = base64.b64decode(rxInfo['gatewayID']).hex()
#     framePort           = sensorPackage['fPort']
#     sensorDictionary =  OrderedDict([
#             ("dateTime"        , str(dateTime)),
#             ("nodeID"          , nodeID),
#             ("sensorID"        , sensorID),
#             ("gatewayID"       , gatewayID),
#             ("rssi"            , rxInfo["rssi"]),
#             ("loRaSNR"         , rxInfo["loRaSNR"]),
#             ("channel"         , rxInfo["channel"] ),
#             ("rfChain"         , rxInfo["rfChain"] ),
#             ("frequency"       , txInfo["frequency"]),
#             ("bandwidth"       , loRaModulationInfo["bandwidth"]),
#             ("spreadingFactor" , loRaModulationInfo["spreadingFactor"] ),
#             ("codeRate"        , loRaModulationInfo["codeRate"] ),
#             ("dataRate"        , sensorPackage['dr']),
#             ("frameCounters"   , sensorPackage['fCnt']),
#             ("framePort"       , framePort),
#             ("base64Data"      , sensorPackage['data']),
#             ("base16Data"      , base16Data),
#             ("devAddr"         , sensorPackage['devAddr']),
#             ("deviceAddDecoded", base64.b64decode(sensorPackage['devAddr'].encode()).hex())
#         ])
#     loRaWriteFinisher("LoRaNodes","Summary",dateTime,sensorDictionary)
#     loRaWriteFinisher(gatewayID,"Summary",dateTime,sensorDictionary)
#     return dateTime,gatewayID,nodeID,sensorID,framePort,base16Data;

# def getPortIndex(portIDIn,portIDs):
#     indexOut = 0
#     for portID in portIDs:
#         if (portIDIn == portID['portID']):
#             return indexOut; 
#         indexOut = indexOut +1
#     return -1;


# def loRaSummaryReceive(message,portIDs):
#     nodeID = message.topic.split('/')[5]
#     sensorPackage       =  decoder.decode(message.payload.decode("utf-8","ignore"))
#     rxInfo              =  sensorPackage['rxInfo'][0]
#     txInfo              =  sensorPackage['txInfo']
#     loRaModulationInfo  =  txInfo['loRaModulationInfo']
#     sensorID            = portIDs[getPortIndex(sensorPackage['fPort'],portIDs)]['sensor']
#     dateTime            = datetime.datetime.fromisoformat(sensorPackage['publishedAt'][0:26])
#     base16Data          = base64.b64decode(sensorPackage['data'].encode()).hex()
#     gatewayID           = base64.b64decode(rxInfo['gatewayID']).hex()
#     framePort           = sensorPackage['fPort']
#     sensorDictionary =  OrderedDict([
#             ("dateTime"        , str(dateTime)),
#             ("nodeID"          , nodeID),
#             ("sensorID"        , sensorID),
#             ("gatewayID"       , gatewayID),
#             ("rssi"            , rxInfo["rssi"]),
#             ("loRaSNR"         , rxInfo["loRaSNR"]),
#             ("channel"         , rxInfo["channel"] ),
#             ("rfChain"         , rxInfo["rfChain"] ),
#             ("frequency"       , txInfo["frequency"]),
#             ("bandwidth"       , loRaModulationInfo["bandwidth"]),
#             ("spreadingFactor" , loRaModulationInfo["spreadingFactor"] ),
#             ("codeRate"        , loRaModulationInfo["codeRate"] ),
#             ("dataRate"        , sensorPackage['dr']),
#             ("frameCounters"   , sensorPackage['fCnt']),
#             ("framePort"       , framePort),
#             ("base64Data"      , sensorPackage['data']),
#             ("base16Data"      , base16Data),
#             ("devAddr"         , sensorPackage['devAddr']),
#             ("deviceAddDecoded", base64.b64decode(sensorPackage['devAddr'].encode()).hex())
#         ])
#     # loRaWriteFinisher("LoRaNodes","Summary",dateTime,sensorDictionary)
#     # loRaWriteFinisher(gatewayID,"Summary",dateTime,sensorDictionary)
#     return dateTime,gatewayID,nodeID,sensorID,framePort,base16Data;