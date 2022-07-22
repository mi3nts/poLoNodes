import datetime
from multiprocessing import Pool, freeze_support
import config as cfg
import pandas as pd
import functions as fn
from pathlib import Path
import shutil
import os


audioFileName      = "mintsAudio"
SaveAudioLoc       = "/home/teamlary/NC/"
minConfidence      = .3
numOfThreads       = 4
labels             = pd.read_csv("labels/labels.csv")
dateTime           =  datetime.datetime.utcnow()
ResultCSVfileloc   = "/home/teamlary/NC/"   


if __name__ == "__main__":
    while True:
        if Path(SaveAudioLoc + audioFileName + '.wav').is_file():
            dateTime = datetime.datetime.utcnow()      
            # Freeze support for excecutable
            freeze_support()
            cfg = fn.configSetUp(cfg,SaveAudioLoc,minConfidence,numOfThreads)
            soundClassData = pd.read_csv(SaveAudioLoc + '/'+ audioFileName+  '.BirdNET.results.csv')
            soundClassData["Labels"] = soundClassData["Scientific name"].map(labels.set_index("Scientific name")["Labels"])

            # insert dateTime column
            time = []
            for index, row in soundClassData.iterrows():
                time_str = str(dateTime + datetime.timedelta(seconds = row['Start (s)']))
                time.append(time_str)
            
            soundClassData.insert(0,'dateTime', time)
        
            #Drop Columns
            soundClassData.drop(['Start (s)' ,'End (s)', 'Scientific name', 'Common name'], inplace=True, axis= 1)

            #Check if the file does not exists then save it, else add the new rows (data) to the existing csv file
            if Path(ResultCSVfileloc +'/' +'BirdNET.results.csv').is_file():
                soundClassData = pd.concat([pd.read_csv(ResultCSVfileloc +'/' +'BirdNET.results.csv'), soundClassData], axis = 0)
                soundClassData.to_csv( ResultCSVfileloc +'/' +'BirdNET.results.csv' , index = False)
            else:
                
                soundClassData.to_csv( ResultCSVfileloc +'/' +'BirdNET.results.csv' , index = False)
            #Delete the audio file after analyzing after analyzing.    
            os.remove(SaveAudioLoc + audioFileName + '.wav')
            print(soundClassData)
    
    

        






        

        




        





    