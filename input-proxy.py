#!/usr/bin/env python3

from re import VERBOSE
from threading import Thread
from queue import Queue
import time
from typing import NamedTuple
from inputs import devices, InputDevice, InputEvent, UnknownEventCode, DeviceManager
import sched
import signal
import os
import argparse
import glob
import yaml
from lib.gamepad import Gamepad
from lib.connection import I2CConnector, I2CConnection

class Device(NamedTuple):
    index: int
    device: InputDevice

class Event(NamedTuple):
    index: int
    ev: InputEvent

 
def producer(queue, relQueue, name: str, index: int):
    if VERBOSE:
        print('Starting Producer ', name, index)
    while True:
        try:
            device = findDevice(name, index)
            id = '%s [%i]' % (name, index)
            while True:
                try:
                    events = device.read()
                    for event in events:
                        if VERBOSE:
                            print('SRC: ', event.device.name, event.code, event.state)
                        if event.ev_type == 'Absolute' or event.ev_type == 'Key':
                            queue.put(Event(index, event))
                        elif event.ev_type == 'Relative':
                            relQueue.put(Event(index, event))
                except UnknownEventCode:
                    pass

        except (OSError, NameError, FileNotFoundError) as err:
            print(err)
            print('reconnecting currently not possible, exiting')
            os._exit(0)
        
 
def consumer(queue):
    while True:
        ev = queue.get() 
        for gp in config.get('gamepads'):
            for d in gp.get('devices'):
                deviceIndex = d.get('index', 0)
                deviceName = d.get('name')
                for b in d.get('bindings'):
                    if b.get('event') == ev.ev.code and ev.ev.device.name == deviceName and ev.index == deviceIndex:
                        bState = b.get('state', -1)
                        if bState > -1:
                            if bState == ev.ev.state:
                                print(gp.get('name'), b.get('invoke'), 1)
                            else:
                                print(gp.get('name'), b.get('invoke'), 0)
                        else:
                            print(gp.get('name'), b.get('invoke'), ev.ev.state)
    
def findDevice(name: str, index: int):
    for d in devices.all_devices:
        if d.name == name:
            if index == 0:
                if VERBOSE:
                    print('Device found: ', d.name, index)
                return d
            else:
                index -= 1
    if VERBOSE:
        print('Device not found:', name)
        print(devices.all_devices)
    raise NameError('Device not found:', name, index)

global relInputEvent
relInputEvent = None

def handleRelativeInput(queue, relQueue, scheduler, resting=False):
    absXY = [127, 127]
    global relInputEvent
    queueIt = False

    if relQueue.empty():
        if not resting:
            resting = True
            queueIt = True
    else:
        resting = False

        while not relQueue.empty():
            ev = relQueue.get_nowait()
            
            relInputEvent = ev
            
            if ev.ev.code == 'REL_X':
                absXY[0] += ev.ev.state
            elif ev.ev.code == 'REL_Y':
                absXY[1] += ev.ev.state

    absXY[0] = min(255, max(0, absXY[0]))
    absXY[1] = min(255, max(0, absXY[1]))

    if relInputEvent != None and ((not resting) or queueIt):
        eventinfoX = {
            "ev_type": "Absolute",
            "state": absXY[0],
            "timestamp": 0,
            "code": "ABS_X"
        }
        eventinfoY = {
            "ev_type": "Absolute",
            "state": absXY[1],
            "timestamp": 0,
            "code": "ABS_Y"
        }
        queue.put(Event(relInputEvent.index, InputEvent(relInputEvent.ev.device, eventinfoX)))
        queue.put(Event(relInputEvent.index, InputEvent(relInputEvent.ev.device, eventinfoY)))
        #print(absXY)
    scheduler.enter(0.05, 1, handleRelativeInput, (queue, relQueue, scheduler, resting, ))

def listDevices():
    print('Available Devices: \n')
    for d in devices.mice + devices.gamepads:
        print(d)

def signal_handler(sig, frame):
    os._exit(0)

def loadConfig(path):
    with open(path, "r") as stream:
        try:
            c = yaml.safe_load(stream)
            return c
        except yaml.YAMLError as exc:
            print(exc)
            os._exit(1)

def initializeControllers():
    ret = []
    connector = I2CConnector(config.i2c_device)
    for gpc in config.gamepads:
        connection = I2CConnection(gpc.address, connector)
        gp = Gamepad(gpc.address)
        ret.append()
    
    return ret
 
def main():
    queue = Queue(5000)
    relQueue = Queue(5000)
    scheduler = sched.scheduler(time.time, time.sleep)
    controllers = initializeControllers(config)
    

    if VERBOSE:
        print(config)
 
    # fire up the both producers and consumers

    producers = [Thread(target=producer, args=(queue, relQueue, d.get('name'), d.get('index', 0) | 0,))
                 for d in config.get('devices')]
    
    consumers = [Thread(target=consumer, args=(queue, ))]

    scheduler.enter(0.05, 1, handleRelativeInput, (queue, relQueue, scheduler, ))
    
    if VERBOSE:
        print('starting producers')
    for p in producers:
        p.start()

    if VERBOSE:
        print('starting consumers')
    for c in consumers:
        c.start()

    signal.signal(signal.SIGINT, signal_handler)

    scheduler.run()
    
 
    # print('joining producers')
    # for p in producers:
    #     p.join()
 
    # # wait for the remaining tasks to be processed
    # print('joining queue')
    # queue.join()
 
    # # cancel the consumers, which are now idle
    # for c in consumers:
    #     c.cancel()



# Instantiate the parser
parser = argparse.ArgumentParser(description='Gamepad Input Proxy')

parser.add_argument('-l',
    '--list',
    action='store_true',
    help='List available devices')

parser.add_argument('-c',
    '--config',
    type=str,
    help='Config directory')

parser.add_argument('-v',
    '--verbose',
    action='store_true',
    help='Verbose Logging enabled')


args = parser.parse_args()

# engine = pyttsx3.init() # object creation
# engine.setProperty('volume',1.0)
# engine.setProperty('rate', 150) 
# engine.say("Monkey Ball")
# engine.say("Mario Kart")
# engine.say("Super Smash Brothers")
# engine.say("Default")
# engine.runAndWait()
# engine.stop()

VERBOSE = False

if args.verbose:
    VERBOSE = True


if args.list:
    listDevices()
else:
    configPath = args.config
    if not args.config:
        print("Please provide the configuration directory")
    else:
        configFiles = glob.glob(os.path.join(args.config, '*.yaml'))
        if len(configFiles) == 0:
            print("No config file found")
        else:
            deviceIndices = {}
            config = loadConfig(configFiles[0])
            configIndex = 0
            main()