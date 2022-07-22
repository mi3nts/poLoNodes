from i2c_as7265x import AS7265X
import i2c_as7265x
import smbus2
import numpy as np
import matplotlib.pyplot as plt

bus = smbus2.SMBus(1)

debug  = False 

while (1):
    try:
        as7265x.takeMeasurements()

        data = []
        data.append(as7265x.getCalibratedA())
        data.append(as7265x.getCalibratedB())
        data.append(as7265x.getCalibratedC())
        data.append(as7265x.getCalibratedD())
        data.append(as7265x.getCalibratedE())
        data.append(as7265x.getCalibratedF())
        data.append(as7265x.getCalibratedG())
        data.append(as7265x.getCalibratedH())
        data.append(as7265x.getCalibratedR())        
        data.append(as7265x.getCalibratedI())
        data.append(as7265x.getCalibratedS())
        data.append(as7265x.getCalibratedJ())
        data.append(as7265x.getCalibratedT())
        data.append(as7265x.getCalibratedU())
        data.append(as7265x.getCalibratedV())
        data.append(as7265x.getCalibratedW())
        data.append(as7265x.getCalibratedK())
        data.append(as7265x.getCalibratedL())
        print(data)

    except:
        break

as7265x.disableBulb(i2c_as7265x.LED_WHITE)
as7265x.disableBulb(i2c_as7265x.LED_IR)
as7265x.disableBulb(i2c_as7265x.LED_UV)