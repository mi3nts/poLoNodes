# MQTT Client demo
# Continuously monitor two different MQTT topics for data,
# check if the received data matches two predefined 'commands'

from traceback import print_tb
import paho.mqtt.client as mqtt
import datetime
import yaml
import collections
import json

# from poLoNodes.firmware.xu4LoRa.mintsXU4 import mintsLoRaSensing as mSR
from mintsXU4 import mintsDefinitions as mD
from mintsXU4 import mintsLoRaSensing as mLS
# from xu4LoRa.mintsXU4 import mintsLoRaReader as mLR
# from xu4LoRa.mintsXU4 import mintsLiveNodes as mLN

import datetime

mqttPortLoRa        = mD.mqttPortLoRa
mqttBrokerLoRa      = mD.mqttBrokerLoRa
loRaCredentials     = mD.loRaCredentials  
nodeIDs             = mD.nodeIDs


tlsCert             = mD.tlsCert
portIDs             = mD.portIDs

connected        = False  # Stores the connection status
broker       = mqttBrokerLoRa  
port         = mqttPortLoRa  # Secure port
mqttUN       = loRaCredentials['username'] 
mqttPW       = loRaCredentials['password'] 
nodeObjects  = []
decoder = json.JSONDecoder(object_pairs_hook=collections.OrderedDict)
print(portIDs)


def getNodeIndex(nodeIDIn):
    indexOut = 0
    for node in nodeIDs:
        nodeID = node['nodeID']
        if (nodeID == nodeIDIn):
            return indexOut; 
        indexOut = indexOut +1
    return -1;

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    topic = "utd/lora/app/2/device/+/event/up"
    client.subscribe(topic)
    print("Subscrbing to Topic: "+ topic)
    for node in nodeIDs:
        print("Appending  Node")
        nodeID = node['nodeID']
        print(nodeID)
        # nodeObjects.append(mLN.node(nodeID))
    
def on_message(client, userdata, msg):
    # try:
        print()
        print(" - - - MINTS DATA RECEIVED - - - ")
        # print(msg.payload)
        dateTime,gatewayID,nodeID,sensorID,framePort,base16Data = \
            mLS.loRaSummaryReceive(msg,portIDs)
        print("Node ID         : " + nodeID)
        nodeIndex = getNodeIndex(nodeID)
        if nodeIndex >= 0 :  
            print("============")
            sensorDictionary = mLS.sensorReceiveLoRa(dateTime,nodeID,sensorID,framePort,base16Data)
            print(sensorDictionary)
            dateTime = datetime.datetime.strptime(sensorDictionary["dateTime"], '%Y-%m-%d %H:%M:%S.%f')
            print("Node ID         : " + nodeID)
            print("Gateway ID      : " + gatewayID)
            print("Sensor ID       : " + sensorID)
            print("Date Time       : " + str(dateTime))
            print("Port ID         : " + str(framePort))
            print("Base 16 Data    : " + base16Data)

    # except Exception as e:
    #     print("[ERROR] Could not publish data, error: {}".format(e))


# Create an MQTT client and attach our routines to it.
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(mqttUN,mqttPW)
client.connect(broker, port, 60)
client.loop_forever()