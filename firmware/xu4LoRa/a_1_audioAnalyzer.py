#from importlib_metadata import files

from scipy.io.wavfile import write
import os

import csv
import json
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

minConfidence      = .3
numOfThreads       = 4

dataFolder        = mD.dataFolder
tmpFolderName     = mD.dataFolderTmp
jsonFolderName    = mD.dataFolderJson


currentIndex = 0 

def main(cfg):
    labels = pd.read_csv("mintsAudio/labels/labels.csv") 

    while True:
        # try:
            audioFolders = glob(tmpFolderName+ "/*/", recursive = True)
            time.sleep(1)
            for folderIn in audioFolders:
                freeze_support()
                cfg = fn.configSetUp(cfg,folderIn,minConfidence,numOfThreads)
                soundClassData = pd.read_csv(folderIn + '/'+ audioFileNamePre+  '.BirdNET.results.csv')
                soundClassData["Labels"] = soundClassData["Scientific name"].map(labels.set_index("Scientific name")["Labels"])
                baseDateTime = folderIn.split('/')
                dateTimeBase  = datetime.datetime.strptime(\
                                baseDateTime[-2], '%Y_%m_%d_%H_%M_%S_%f')
        
                for index, row in soundClassData.iterrows():
                    dateTimeCurrent = str(dateTimeBase + datetime.timedelta(seconds = row['Start (s)']))
                    sensorDictionary = OrderedDict([
                        ("label"        ,row['Labels']),
                        ("confidence"   ,row['Confidence'])
                        ])
                    print(sensorDictionary)
                    print(dateTimeCurrent)    
                    with open(fn.getJsonFileName(folderIn,dateTimeCurrent), "w") as outfile:
                        json.dump(sensorDictionary, outfile)
           

               

      


if __name__ == "__main__":
    print("=============")
    print("    MINTS    ")
    print("=============")
    # print("Connecting to the microphone on Channel: {0}".format(channelSelected) + " with Sample Rate " + str(sampleRate))
    main(cfg)    








