
import os
import sounddevice as sd
from scipy.io.wavfile import write

sampleRate         = 44100  # Sample rate
audioLength        = 120 # Duration of recording
channelSelected    = 1
audioFileName      = "mintsAudio" # Audio file name
SaveAudioLoc       = "/home/teamlary/NC/" # Audio file is saved here

def makeAudioFile(sampleRate,audioLength,channelSelected,audioFileName, SaveAudioLoc):
    
    recording = sd.rec(int(audioLength * sampleRate), samplerate=sampleRate, channels=channelSelected)
    sd.wait()  # Wait until recording is finished
    write(os.path.join(SaveAudioLoc,audioFileName), sampleRate, recording)  # Save as WAV file
    return recording;

while True:
    print("Recording Audio for "+ str(audioLength) + " Seconds")
    makeAudioFile(sampleRate,audioLength,channelSelected,audioFileName+ ".wav",SaveAudioLoc)
            
            