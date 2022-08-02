#!/bin/bash
sleep 40


kill $(pgrep -f 'python3 l_1_loRaSend.py')
sleep 5
python3 l_1_loRaSend.py 0

