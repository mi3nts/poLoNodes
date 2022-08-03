import sounddevice as sd
from scipy.io.wavfile import write
import os

import csv

import os
import sys

import argparse
import datetime


from multiprocessing import Pool, freeze_support

import numpy as np

import config as cfg
import pandas as pd

import functions as fn

fs = 44100  # Sample rate
seconds = 9  # Duration of recording

"""

while True:
    folder1 = datetime.now().strftime("MINTS/%Y")
    folder2 = datetime.now().strftime('MINTS/%Y/%m')
    folder3 = datetime.now().strftime('MINTS/%Y/%m/%d')
    if not os.path.exists(os.path.join(folder1)):
        os.mkdir(os.path.join(folder1))
        if not os.path.exists(os.path.join(folder2)):
            os.mkdir(os.path.join(folder2))
            if not os.path.exists(os.path.join(folder3)):
                os.mkdir(os.path.join(folder3))
    date = datetime.now().strftime("%Y_%m_%d-%I:%M:%S_%p")
    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
    sd.wait()  # Wait until recording is finished
    write(os.path.join(folder3, f"{date}.wav"), fs, myrecording)  # Save as WAV file
    time.sleep(10)
"""





if __name__ == '__main__':

    while True:
        #date = datetime.datetime.now().strftime("%Y_%m_%d-%I:%M:%S_%p")
        myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
        sd.wait()  # Wait until recording is finished
        write(os.path.join("NC/", "Audio.wav"), fs, myrecording)  # Save as WAV file
        



        # Freeze support for excecutable
        freeze_support()

        # Clear error log
        #clearErrorLog()

        # Parse arguments
        parser = argparse.ArgumentParser(description='Analyze audio files with BirdNET')
        parser.add_argument('--i', default='NC/', help='Path to input file or folder. If this is a file, --o needs to be a file too.')
        parser.add_argument('--o', default='NC/', help='Path to output file or folder. If this is a file, --i needs to be a file too.')
        parser.add_argument('--lat', type=float, default=-1, help='Recording location latitude. Set -1 to ignore.')
        parser.add_argument('--lon', type=float, default=-1, help='Recording location longitude. Set -1 to ignore.')
        parser.add_argument('--week', type=int, default=-1, help='Week of the year when the recording was made. Values in [1, 48] (4 weeks per month). Set -1 for year-round species list.')
        parser.add_argument('--slist', default='', help='Path to species list file or folder. If folder is provided, species list needs to be named \"species_list.txt\". If lat and lon are provided, this list will be ignored.')
        parser.add_argument('--sensitivity', type=float, default=1.0, help='Detection sensitivity; Higher values result in higher sensitivity. Values in [0.5, 1.5]. Defaults to 1.0.')
        parser.add_argument('--min_conf', type=float, default=0.3, help='Minimum confidence threshold. Values in [0.01, 0.99]. Defaults to 0.1.')
        parser.add_argument('--overlap', type=float, default=0.0, help='Overlap of prediction segments. Values in [0.0, 2.9]. Defaults to 0.0.')
        parser.add_argument('--rtype', default='csv', help='Specifies output format. Values in [\'table\', \'audacity\', \'r\', \'csv\']. Defaults to \'table\' (Raven selection table).')
        parser.add_argument('--threads', type=int, default=4, help='Number of CPU threads.')
        parser.add_argument('--batchsize', type=int, default=1, help='Number of samples to process at the same time. Defaults to 1.')
        parser.add_argument('--locale', default='en', help='Locale for translated species common names. Values in [\'af\', \'de\', \'it\', ...] Defaults to \'en\'.')
        parser.add_argument('--sf_thresh', type=float, default=0.03, help='Minimum species occurrence frequency threshold for location filter. Values in [0.01, 0.99]. Defaults to 0.03.')

        args = parser.parse_args()

        # Set paths relative to script path (requested in #3)
        cfg.MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), cfg.MODEL_PATH)
        cfg.LABELS_FILE = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), cfg.LABELS_FILE)
        cfg.TRANSLATED_LABELS_PATH = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), cfg.TRANSLATED_LABELS_PATH)
        cfg.MDATA_MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), cfg.MDATA_MODEL_PATH)
        cfg.CODES_FILE = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), cfg.CODES_FILE)
        cfg.ERROR_LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), cfg.ERROR_LOG_FILE)

        # Load eBird codes, labels
        cfg.CODES = fn.loadCodes()
        cfg.LABELS = fn.loadLabels(cfg.LABELS_FILE)

        # Load translated labels
        lfile = os.path.join(cfg.TRANSLATED_LABELS_PATH, os.path.basename(cfg.LABELS_FILE).replace('.txt', '_{}.txt'.format(args.locale)))
        if not args.locale in ['en'] and os.path.isfile(lfile):
            cfg.TRANSLATED_LABELS = fn.loadLabels(lfile)
        else:
            cfg.TRANSLATED_LABELS = cfg.LABELS   

        ### Make sure to comment out appropriately if you are not using args. ###

        # Load species list from location filter or provided list
        cfg.LATITUDE, cfg.LONGITUDE, cfg.WEEK = args.lat, args.lon, args.week
        cfg.LOCATION_FILTER_THRESHOLD = max(0.01, min(0.99, float(args.sf_thresh)))
        if cfg.LATITUDE == -1 and cfg.LONGITUDE == -1:
            if len(args.slist) == 0:
                cfg.SPECIES_LIST_FILE = None
            else:
                cfg.SPECIES_LIST_FILE = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), args.slist)
                if os.path.isdir(cfg.SPECIES_LIST_FILE):
                    cfg.SPECIES_LIST_FILE = os.path.join(cfg.SPECIES_LIST_FILE, 'species_list.txt')
            cfg.SPECIES_LIST = fn.loadSpeciesList(cfg.SPECIES_LIST_FILE)
        else:
            fn.predictSpeciesList()
        if len(cfg.SPECIES_LIST) == 0:
            print('Species list contains {} species'.format(len(cfg.LABELS)))
        else:        
            print('Species list contains {} species'.format(len(cfg.SPECIES_LIST)))

        # Set input and output path    
        cfg.INPUT_PATH = args.i
        cfg.OUTPUT_PATH = args.o

        # Parse input files
        if os.path.isdir(cfg.INPUT_PATH):
            cfg.FILE_LIST = fn.parseInputFiles(cfg.INPUT_PATH)  
        else:
            cfg.FILE_LIST = [cfg.INPUT_PATH]

        # Set confidence threshold
        cfg.MIN_CONFIDENCE = max(0.01, min(0.99, float(args.min_conf)))

        # Set sensitivity
        cfg.SIGMOID_SENSITIVITY = max(0.5, min(1.0 - (float(args.sensitivity) - 1.0), 1.5))

        # Set overlap
        cfg.SIG_OVERLAP = max(0.0, min(2.9, float(args.overlap)))

        # Set result type
        cfg.RESULT_TYPE = args.rtype.lower()    
        if not cfg.RESULT_TYPE in ['table', 'audacity', 'r', 'csv']:
            cfg.RESULT_TYPE = 'table'

        # Set number of threads
        if os.path.isdir(cfg.INPUT_PATH):
            cfg.CPU_THREADS = max(1, int(args.threads))
            cfg.TFLITE_THREADS = 1
        else:
            cfg.CPU_THREADS = 1
            cfg.TFLITE_THREADS = max(1, int(args.threads))

        # Set batch size
        cfg.BATCH_SIZE = max(1, int(args.batchsize))

        # Add config items to each file list entry.
        # We have to do this for Windows which does not
        # support fork() and thus each process has to
        # have its own config. USE LINUX!
        flist = []
        for f in cfg.FILE_LIST:
            flist.append((f, cfg.getConfig()))

        # Analyze files   
        if cfg.CPU_THREADS < 2:
            for entry in flist:
                fn.analyzeFile(entry)
        else:
            with Pool(cfg.CPU_THREADS) as p:
                p.map(fn.analyzeFile, flist)


        #add the time coloumn.
        t = datetime.datetime.now().strftime("%Y_%m_%d,%H:%M:%S")

        df = pd.read_csv('NC/Audio.BirdNET.results.csv')
        df.insert(0,'Date', t)
        
        df.to_csv("NC/Audio.BirdNET.results.csv", index = False)

        #creat the final csv file.
        if not os.path.exists('NC/final.csv'):
            with open('NC/final.csv', "w+", newline='') as ffile:
                writer = csv.writer(ffile)
                writer.writerow(["Date", "Start (s)","End (s)", "Scientific name","Common name","Confidence"])
        lis = ['NC/final.csv', 'NC/Audio.BirdNET.results.csv' ]
        Result = pd.concat( [ pd.read_csv(ff) for ff in lis ] )
        Result.to_csv( "NC/final.csv", index= False )

        #Add Label Column to the csv.
        lbl = pd.read_csv("NC/final.csv")
        lbl["Labels"] = ""
        lbl.to_csv("NC/final.csv", index=False)
        

        # Get label values from labels.csv 
        df1 = pd.read_csv("labels/labels.csv")  
        df2 = pd.read_csv("NC/final.csv")
        df2["Labels"] = df2["Scientific name"].map(df1.set_index("Scientific name")["Labels"])
        df2.to_csv("NC/final.csv", index=False)
        mv_lbl = pd.read_csv("NC/final.csv")
        df_lbl = mv_lbl.pop("Labels")
        mv_lbl.insert(2,"Labels",df_lbl)
        mv_lbl.to_csv("NC/final.csv", index= False)


        #Drop Columns
        drop_col = pd.read_csv('NC/final.csv')
        drop_col.drop(['End (s)', 'Scientific name', 'Common name'], inplace=True, axis= 1)
        drop_col.to_csv('NC/final_result.csv', index = False)

            


        




        





    
