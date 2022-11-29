#!/bin/bash
sleep 40
rm -r /home/teamlary/mintsDataTmp/*
sleep 1
rm /home/teamlary/mintsDataJson/*
sleep 10
kill $(pgrep -f 'python3 a_1_audioRecorder.py')
sleep 5
python3 a_1_audioRecorder.py &
sleep 5

kill $(pgrep -f 'python3 l_1_loRaSend.py')
sleep 5
python3 l_1_loRaSend.py &
sleep 5

kill $(pgrep -f 'a_2_audioAnalyzer.py')
sleep 5
python3 a_2_audioAnalyzer.py &
sleep 5

