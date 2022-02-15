from typing import NamedTuple

from lib.config import DeviceConfig
from inputs import InputDevice, InputEvent


class Device(NamedTuple):
    deviceConfig: DeviceConfig
    device: InputDevice


class Event(NamedTuple):
    deviceConfig: DeviceConfig
    payload: InputEvent

