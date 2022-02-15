#!/usr/bin/env python3

from threading import Thread
from queue import Queue
import time
from inputs import devices, InputDevice, InputEvent, UnknownEventCode, DeviceManager
import sched
import signal
import os
import argparse
import glob
import yaml
from lib.config import INVALID, Configuration, DeviceConfig
from lib.eventdispatcher import EventDispatcher, Event
from lib.gamepad import Gamepad
from lib.connection import Connection, DummyConnection, I2CConnection, I2CConnector

import sys
print(sys.path)




class AnalogConfig():
    MULT_X: float
    MULT_Y: float
    INVERT_X: bool  # TODO: implement
    INVERT_Y: bool  # TODO: implement
    RELATIVE: bool

    def __init__(self, cfg: dict):
        self.MULT_X = cfg.get('MULT_X', cfg.get('MULT', 4.0))
        self.MULT_Y = cfg.get('MULT_Y', cfg.get('MULT', 4.0))
        self.INVERT_X = cfg.get('INVERT_X', False)
        self.INVERT_Y = cfg.get('INVERT_Y', False)
        self.RELATIVE = cfg.get('RELATIVE', True)


def producer(dispatcher: EventDispatcher, relQueue: Queue[Event], deviceConfig: DeviceConfig):
    if VERBOSE:
        print('Starting Producer ', deviceConfig)
    while True:
        try:
            device = find_device(deviceConfig)
            while True:
                try:
                    events = device.read()
                    for event in events:
                        dispatcher.handleEvent(deviceConfig, event, verbose_logging = args.benchmark or VERBOSE)
                except UnknownEventCode:
                    pass

        except (OSError, NameError, FileNotFoundError) as err:
            print(err)
            print('reconnecting currently not possible, exiting')
            os._exit(0)


def consumer(queue: Queue[Event], config: Configuration):
    connector: I2CConnector
    if not DUMMY:
        connector = I2CConnector(config.i2c_device)

    gamepads = { a : Gamepad(DummyConnection(hex(a)) if DUMMY else I2CConnection(a, connector)) for a in config.addresses }

    while True:
        ev = queue.get()
        try:
            bindings = ev.deviceConfig.mappings.get(ev.payload.code, [])
            for b in bindings:
                g = gamepads[b.address]
                
                if b.state == INVALID:
                    g.event(b.invoke, ev.payload.state)
                elif b.state == ev.payload.state:
                    g.event(b.invoke, 1)
                else:
                    g.event(b.invoke, 0)
            
            if len(bindings) == 0:
                print('unconfigured event:', str(ev.deviceConfig), ev.payload.code)

        except Exception as err:
            print('Error: ', err)
            raise err


def find_device(deviceConfig: DeviceConfig):
    index = deviceConfig.index
    miceAndGamepads = devices.mice + devices.gamepads
    sortedDevices = sorted(
        miceAndGamepads, key=InputDevice.get_char_device_path)
    for d in sortedDevices:
        if d.name == deviceConfig.name:
            if index == 0:
                if VERBOSE:
                    print('Device found: ', d.name, deviceConfig.index)
                return d
            else:
                index -= 1
    if VERBOSE:
        print('Device not found:', deviceConfig.name)
        print(sortedDevices)
    raise NameError('Device not found:', deviceConfig.name, deviceConfig.index)



def listDevices():
    print('Available Devices: \n')
    for d in devices.mice + devices.gamepads:
        print(d)


def signal_handler(sig, frame):
    os._exit(0)


def loadConfig(base_config, config_path):
    try:
        return Configuration.load(base_config, config_path)
    except yaml.YAMLError as exc:
        print(exc)
        os._exit(1)

def update(dispatcher: EventDispatcher, scheduler: sched.scheduler):
    dispatcher.update()
    scheduler.enter(0.06, 1, update, (dispatcher, scheduler, ))


def main():
    queue = Queue[Event](5000)
    relQueue = Queue[Event](5000)
    scheduler = sched.scheduler(time.time, time.sleep)

    if VERBOSE:
        print('Config: ')
        print(config)

    dispatcher = EventDispatcher(config, queue)

    # fire up the both producers and consumers

    producers = [Thread(target=producer, args=(dispatcher, relQueue, device,))
                 for device in config.devices]

    consumers = [Thread(target=consumer, args=(queue, config, ))]

    update(dispatcher, scheduler)

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

    if VERBOSE:
        print('joining producers')
    for p in producers:
        p.join()

    # wait for the remaining tasks to be processed
    if VERBOSE:
        print('joining queue')
    queue.join()

    # cancel the consumers, which are now idle
    for c in consumers:
        c.cancel()


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

parser.add_argument('-g',
                    '--glob',
                    type=str,
                    help='Global Configuration')

parser.add_argument('-v',
                    '--verbose',
                    action='store_true',
                    help='Verbose Logging enabled')

parser.add_argument('-b',
                    '--benchmark',
                    action='store_true',
                    help='Log the input events with timestamp')

parser.add_argument('-d',
                    '--dummy',
                    action='store_true',
                    help='Use a dummy outbound connection for debug purposes')


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

VERBOSE = args.verbose
DUMMY = args.dummy

if args.list:
    listDevices()
else:
    configPath = args.config
    if not args.config:
        print("Please provide the configuration directory")
    else:
        configFiles = glob.glob(os.path.join(args.config, '*.yaml'))
        global_config = args.glob
        if len(configFiles) == 0 and len(global_config) == 0:
            print("No config file found")
        else:
            config = loadConfig(global_config, configFiles[0])
            configIndex = 0
            main()
