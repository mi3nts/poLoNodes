#!/bin/bash
sleep 40

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

