from pprint import pprint
from typing import NamedTuple

from lib.config import DeviceConfig
from inputs import InputDevice, InputEvent

def trace(d: dict):
    pprint({k: (str(v) + ' ' + str(type(v))) for k, v in d.items() })


class Device(NamedTuple):
    deviceConfig: DeviceConfig
    device: InputDevice


class Event(NamedTuple):
    deviceConfig: DeviceConfig
    payload: InputEvent

