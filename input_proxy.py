#!/usr/bin/env python3

from threading import Thread
from queue import Queue
import time
from typing import List, NamedTuple
from inputs import devices, InputDevice, UnknownEventCode
import sched
import signal
import os
import argparse
import glob
import yaml
from lib.config import INVALID, Configuration, ConfigurationProvider, DeviceConfig
from lib.display_connection import DisplayConnectionClient
from lib.eventdispatcher import EventDispatcher, Event
from lib.gamepad import Gamepad
from lib.connection import DummyConnection, I2CConnection, I2CConnector

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

                state = ev.payload.state
                
                if b.state == ev.payload.state:
                    state = 1 if b.invoke_state == INVALID else b.invoke_state
                else:
                    state = 0 if b.zero_pos == INVALID else b.zero_pos
                
                g.event(b.invoke, state, verbose_output=VERBOSE)
            
            if len(bindings) == 0:
                print('unconfigured event:', str(ev.deviceConfig), ev.payload.code)

        except Exception as err:
            print('Error: ', err)
            raise err


def find_device(deviceConfig: DeviceConfig) -> InputDevice:
    index = deviceConfig.index
    miceAndGamepads: List[InputDevice] = devices.mice + devices.gamepads
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


def loadConfig(base_config, config_path, display_cmd = 'down'):
    try:
        c = Configuration.load(base_config, config_path)
        
        display = DisplayConnectionClient()
        display.send(display_cmd, c.name)

        return c
    except yaml.YAMLError as exc:
        print(exc)
        os._exit(1)

def update(dispatcher: EventDispatcher, scheduler: sched.scheduler):
    dispatcher.update()
    scheduler.enter(0.06, 1, update, (dispatcher, scheduler, ))

class IndexItem():
    def __init__(self, value):
        self._value = value
    
    def value(self):
        return self._value
    
    def set_value(self, value: int):
        self._value = value
        

def main():
    queue = Queue[Event](5000)
    relQueue = Queue[Event](5000)
    scheduler = sched.scheduler(time.time, time.sleep)

    
    configFiles = glob.glob(os.path.join(args.config, '*.yaml'))
    configFiles.sort()
    configIndex = IndexItem(0)
    global_config = args.glob
    if len(configFiles) == 0 and len(global_config) == 0:
        print("No config file found")
        exit(1)
    else:
        config = loadConfig(global_config, configFiles[0])

    config_provider = ConfigurationProvider(config)

    if VERBOSE:
        print('Config: ')
        print(config)

    dispatcher = EventDispatcher(config_provider, queue)

    dispatcher.register_menu_listener('NEXT_CONFIG', lambda: (
        configIndex.set_value((configIndex.value() + 1) % len(configFiles)),
        config_provider.change_config(loadConfig(global_config, configFiles[configIndex.value()]))
    ))

    dispatcher.register_menu_listener('PREV_CONFIG', lambda: (
        configIndex.set_value(len(configFiles) - 1 if configIndex.value() == 0 else configIndex.value() - 1),
        config_provider.change_config(loadConfig(global_config, configFiles[configIndex.value()], display_cmd='up'))
    ))

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
elif not args.config:
    print("Please provide the configuration directory")
else:
    main()