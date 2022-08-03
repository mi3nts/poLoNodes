#from importlib_metadata import files

from scipy.io.wavfile import write
import os

import csv

import sys
from collections import OrderedDict
import datetime

import numpy as np
import pandas as pd
from glob import glob

import time

time.sleep(1) 

from mintsXU4 import mintsLoRaSensing as mSR
from mintsXU4 import mintsDefinitions as mD

from multiprocessing import Pool, freeze_support
from mintsAudio import config as cfg
from mintsAudio import functions as fn

sampleRate         = 44100  # Sample rate
period             = 120    # Duration of recording
channelSelected    = 1
audioFileNamePre   = "mintsAudio"
tmpFolderName     = mD.dataFolderTmp
minConfidence      = .3
numOfThreads       = 4

dataFolder         = mD.dataFolder

currentIndex = 0 

def main(cfg):
    labels = pd.read_csv("mintsAudio/labels/labels.csv") 
    

    while True:
        # try:
            audioFolders = glob(tmpFolderName+ "/*/", recursive = True)
            time.sleep(1)
            print(audioFolders)
            for folderIn in audioFolders:
                # freeze_support()
                # cfg = fn.configSetUp(cfg,folderIn,minConfidence,numOfThreads)
                # soundClassData = pd.read_csv(folderIn + '/'+ audioFileNamePre+  '.BirdNET.results.csv')
                # soundClassData["Labels"] = soundClassData["Scientific name"].map(labels.set_index("Scientific name")["Labels"])
                # print(soundClassData)

                baseDateTime = folderIn.split('/')
                print(baseDateTime[-2])
                dateTime  = datetime.datetime.strptime( baseDateTime[-2], '%Y_%m_%d_%H_%M_%S_%f')
                print(dateTime)
                # Get Date Time From the File
                # Save it as .json with proper time for its name 
                # The json files should be under mintsData/jsonAudio/dateTimeFileName
                # delete the folder 
            
     
            #     for index, row in soundClassData.iterrows():
            #         sensorDictionary = OrderedDict([
            #             ("dateTime"     ,str(dateTime + datetime.timedelta(seconds = row['Start (s)']))),
            #             ("label"        ,row['Labels']),
            #             ("confidence"   ,row['Confidence'])
            #             ])
            # #     mSR.sensorFinisher(dateTime,"MBC001",sensorDictionary)    

            # Read All the folder names 


            # Freeze support for excecutable
            # freeze_support()
            # cfg = fn.configSetUp(cfg,tmpFolderName,minConfidence,numOfThreads)
            # soundClassData = pd.read_csv(tmpFolderName + '/'+ audioFileNamePre+  '.BirdNET.results.csv')
            # soundClassData["Labels"] = soundClassData["Scientific name"].map(labels.set_index("Scientific name")["Labels"])
            # print(soundClassData)
            # for index, row in soundClassData.iterrows():
            #     sensorDictionary = OrderedDict([
            #         ("dateTime"     ,str(dateTime + datetime.timedelta(seconds = row['Start (s)']))),
            #         ("label"        ,row['Labels']),
            #         ("confidence"   ,row['Confidence'])
            #          ])
            #     mSR.sensorFinisher(dateTime,"MBC001",sensorDictionary)
            print("=============")            
         
        # except OSError as e:
        #     print ("Error: %s - %s." % (e.filename, e.strerror))
        #     print("Microphone Not Connected: Check connection")

               

      


if __name__ == "__main__":
    print("=============")
    print("    MINTS    ")
    print("=============")
    # print("Connecting to the microphone on Channel: {0}".format(channelSelected) + " with Sample Rate " + str(sampleRate))
    main(cfg)    








