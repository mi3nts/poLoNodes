#!/usr/bin/python
# ***************************************************************************
#   I2CPythonMints
#   ---------------------------------
#   Written by: Lakitha Omal Harindha Wijeratne
#   - for -
#   MINTS :  Multi-scale Integrated Sensing and Simulation
#     & 
#   TRECIS: Texas Research and Education Cyberinfrastructure Services
#
#   ---------------------------------
#   Date: July 7th, 2022
#   ---------------------------------
#   This module is written for generic implimentation of MINTS projects
#   --------------------------------------------------------------------------
#   https://github.com/mi3nts
#   https://trecis.cyberinfrastructure.org/
#   http://utdmints.info/
#  ***************************************************************************


#import SI1132
from i2c_scd30 import SCD30
from i2c_as7265x import AS7265X

import sys
import time
import os
import smbus2

debug  = False 

bus     = smbus2.SMBus(0)
scd30   = SCD30(bus,debug)
as7265x = AS7265X(bus,debug)

def main():
    scd30_valid    = scd30.initiate(30)
    as7265x_valid  = as7265x.initiate()
    while True:
        try:
            print("======== SCD30 ========")
            if scd30_valid:
                scd30.read()
            print("=======================")
            time.sleep(2.5)
            print("======= AS7265X =======")
            if as7265x_valid:
                as7265x.read()
            print("=======================")
            time.sleep(2.5)
        except:
            break   
        
    as7265x.shut_down()

if __name__ == "__main__":
   main()