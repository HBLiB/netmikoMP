#!/usr/bin/env python3

import warnings
from cryptography.utils import CryptographyDeprecationWarning
with warnings.catch_warnings():
    warnings.filterwarnings('ignore', category=CryptographyDeprecationWarning)
    import paramiko
import getpass
import json
from netmiko import ConnectHandler
from jumpssh import SSHSession
import numpy as np
import threading
import time
#import datetime
import random
from netmiko.ssh_autodetect import SSHDetect
from netmiko.ssh_dispatcher import ConnectHandler
import threading
import numpy as np

user = input("Enter your username: ")
print("Enter your password")
password = getpass.getpass()
bastionServer = 'IP_JUMPHOST'

baseDir = "/home/hbl/miko/"
devicesRaw = []
devices = {}
finalDevices = {}
notReachable  = []


# txt file with the devices where each device on a new line
with open('devices.list') as f:
    devicesRaw = f.readlines()
   
#Create device dictonary for netmiko to use per device from the text file of devices
for entry in devicesRaw:
    entry = entry.strip()
    devices[entry] = {
    "device_type": "autodetect",
    "host": entry,
    "username": user,
    "password": password,
    #"conn_timeout": 10,
    #"timeout": 60,
    #"session_timeout": 60,
    #"blocking_timeout": 60,
    "ssh_config_file": baseDir + "jumphost.conf"
    }

#Guessing of OS of the device, going through a list of device names based on the device dictonary previously created
def guessOS(dList,dDict,dFinal,dNotReachable):
    for host in dList:
        try:
            guess = SSHDetect(**dDict[host])
            best_match = guess.autodetect()
            dFinal[host] = {
            "device_type": best_match ,
            "host": host,
            "username": "username",
            "password": "password",
            "conn_timeout": 20,
            "timeout": 20,
            "ssh_config_file": baseDir + "jumphost.conf"
            }
        except Exception as err:
            exception_type = type(err).__name__
            print(exception_type)
            dNotReachable.append(host)
        except OSError as error :
            print(error)
            dNotReachable.append(host)


# We split the original list of devices in to 20 new arrays, And assign 1 of the newly created arrays to a thread.
# Meaning 20 threads with each a list of devices.

devList = list(devices.keys())
for array in np.array_split(devList,20):
    t= threading.Thread(target = guessOS, args=(array,devices,finalDevices,notReachable,))
    t.start()
    threads.append(t)

#After starting the threads, we join them back to the main process and wait for them to finish to save the output dictonaries as a file
for t in threads:
    t.join()

with open(baseDir + r'unreachableALL.list', 'w') as fp:
    for item in notReachable:
        fp.write("%s\n" % item)
    print('Done')

with open(baseDir + "NetmikoDevices" +'.json', 'w') as fp:
    json.dump(finalDevices, fp)
    
#Now we indexed all devices per OS to be able load in and use in other "command" scripts. 
