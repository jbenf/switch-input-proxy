"""This module handles the interface to a i2c switch controller"""

from typing import NamedTuple
from lib.connection import Connection


class Registers(NamedTuple):
    """i2c Registers"""
    BTN_0 = 0x0
    BTN_1 = 0x1
    HAT = 0x2
    LX = 0x3
    LY = 0x4
    RX = 0x5
    RY = 0x6


class Btn0Mask(NamedTuple):
    """Bit Indices for the first register"""
    MINUS = 2**0
    PLUS = 2**1
    LCLICK = 2**2
    RCLICK = 2**3
    HOME = 2**4
    CAPTURE = 2**5


class Btn1Mask(NamedTuple):
    """Bit Indices for the second register"""
    Y = 2**0
    B = 2**1
    A = 2**2
    X = 2**3
    L = 2**4
    R = 2**5
    ZL = 2**6
    ZR = 2**7


class HatMask(NamedTuple):
    """Indices for the hat register"""
    DPAD_UP = 2**0
    DPAD_RIGHT = 2**1
    DPAD_DOWN = 2**2
    DPAD_LEFT = 2**3


class HatValues(NamedTuple):
    """hat values"""
    UP = 0x00
    UP_RIGHT = 0x01
    RIGHT = 0x02
    DOWN_RIGHT = 0x03
    DOWN = 0x04
    DOWN_LEFT = 0x05
    LEFT = 0x06
    UP_LEFT = 0x07
    CENTER = 0x08

# Mapping of source dpad values to hat values
hat_map = {
    HatMask.DPAD_UP: HatValues.UP,
    HatMask.DPAD_UP | HatMask.DPAD_RIGHT: HatValues.UP_RIGHT,
    HatMask.DPAD_RIGHT: HatValues.RIGHT,
    HatMask.DPAD_DOWN | HatMask.DPAD_RIGHT: HatValues.DOWN_RIGHT,
    HatMask.DPAD_DOWN: HatValues.DOWN,
    HatMask.DPAD_DOWN | HatMask.DPAD_LEFT: HatValues.DOWN_LEFT,
    HatMask.DPAD_LEFT: HatValues.LEFT,
    HatMask.DPAD_UP | HatMask.DPAD_LEFT: HatValues.UP_LEFT,
}


class AnalogValues(NamedTuple):
    """Special Analog Values"""
    CENTER = 0x80


def handle_btn_0(self, mask: int, state: int):
    """Handle events for the first register"""
    if state == 1:
        self.bitmap_BTN_0 = self.bitmap_BTN_0 | mask
    else:
        self.bitmap_BTN_0 = self.bitmap_BTN_0 & ~ mask

    self.connection.write(Registers.BTN_0, [self.bitmap_BTN_0])


def handle_btn_1(self, mask: int, state: int):
    """Handle events for the second register"""
    if state == 1:
        self.bitmap_BTN_1 = self.bitmap_BTN_1 | mask
    else:
        self.bitmap_BTN_1 = self.bitmap_BTN_1 & ~ mask

    self.connection.write(Registers.BTN_1, [self.bitmap_BTN_1])


def handle_hat(self, mask: int, state: int):
    """Handle events for the hat register"""
    if state == 1:
        self.bitmap_HAT = self.bitmap_HAT | mask
    else:
        self.bitmap_HAT = self.bitmap_HAT & ~mask

    bitmap = hat_map.get(self.bitmap_HAT, HatValues.CENTER)

    if bitmap == HatValues.CENTER:
        self.bitmap_HAT = 0

    self.connection.write(Registers.HAT, [bitmap])


def set_relative_lx(self, state: int):
    """update the x axis of the left analog stick"""
    self.bitmap_LX = min(255, max(0, self.bitmap_LX + state))
    self.connection.write(Registers.LX, [self.bitmap_LX])


def set_relative_ly(self, state: int):
    """update the y axis of the left analog stick"""
    self.bitmap_LY = min(255, max(0, self.bitmap_LY + state))
    self.connection.write(Registers.LY, [self.bitmap_LY])


def set_relative_rx(self, state: int):
    """update the x axis of the right analog stick"""
    self.bitmap_RX = min(255, max(0, self.bitmap_RX + state))
    self.connection.write(Registers.RX, [self.bitmap_RX])


def set_relative_ry(self, state: int):
    """update the y axis of the right analog stick"""
    self.bitmap_RY = min(255, max(0, self.bitmap_RY + state))
    self.connection.write(Registers.RY, [self.bitmap_RY])


def center_analog(self):
    """set the absolute analog values to center"""
    self.bitmap_LX = AnalogValues.CENTER
    self.bitmap_LY = AnalogValues.CENTER
    self.bitmap_RX = AnalogValues.CENTER
    self.bitmap_RY = AnalogValues.CENTER

    self.connection.write(Registers.LX, [self.bitmap_LX])
    self.connection.write(Registers.LY, [self.bitmap_LY])
    self.connection.write(Registers.RX, [self.bitmap_RX])
    self.connection.write(Registers.RY, [self.bitmap_RY])


def set_absolute_analog(self, register: int, state: int):
    """set absolute analog values to a register"""
    self.connection.write(register, [state])


class Gamepad():
    """This class maps input events to nintendo switch controller events and sends them via i2c"""

    bitmap_BTN_0 = 0x00
    bitmap_BTN_1 = 0x00
    bitmap_HAT = 0x00
    bitmap_LX = AnalogValues.CENTER
    bitmap_LY = AnalogValues.CENTER
    bitmap_RX = AnalogValues.CENTER
    bitmap_RY = AnalogValues.CENTER

    def __init__(self, connection: Connection):
        self.connection = connection

    def event(self, invoke: str, state: int):
        """handle a input event"""
        func = self.handling.get(invoke, None)
        if func is not None:
            func(self, state)
        else:
            print('Unkown Event: ', invoke)

    # Event mappings
    handling = {
        'A': lambda self, state: handle_btn_1(self, Btn1Mask.A, state),
        'B': lambda self, state: handle_btn_1(self, Btn1Mask.B, state),
        'X': lambda self, state: handle_btn_1(self, Btn1Mask.X, state),
        'Y': lambda self, state: handle_btn_1(self, Btn1Mask.Y, state),
        'L': lambda self, state: handle_btn_1(self, Btn1Mask.L, state),
        'R': lambda self, state: handle_btn_1(self, Btn1Mask.R, state),
        'ZL': lambda self, state: handle_btn_1(self, Btn1Mask.ZL, state),
        'ZR': lambda self, state: handle_btn_1(self, Btn1Mask.ZR, state),
        'MINUS': lambda self, state: handle_btn_0(self, Btn0Mask.MINUS, state),
        'PLUS': lambda self, state: handle_btn_0(self, Btn0Mask.PLUS, state),
        'HOME': lambda self, state: handle_btn_0(self, Btn0Mask.HOME, state),
        'LCLICK': lambda self, state: handle_btn_0(self, Btn0Mask.LCLICK, state),
        'RCLICK': lambda self, state: handle_btn_0(self, Btn0Mask.RCLICK, state),
        'CAPTURE': lambda self, state: handle_btn_0(self, Btn0Mask.CAPTURE, state),
        'DPAD_UP': lambda self, state: handle_hat(self, HatMask.DPAD_UP, state),
        'DPAD_RIGHT': lambda self, state: handle_hat(self, HatMask.DPAD_RIGHT, state),
        'DPAD_DOWN': lambda self, state: handle_hat(self, HatMask.DPAD_DOWN, state),
        'DPAD_LEFT': lambda self, state: handle_hat(self, HatMask.DPAD_LEFT, state),
        'LX': lambda self, state: set_absolute_analog(self, Registers.LX, state),
        'LY': lambda self, state: set_absolute_analog(self, Registers.LY, state),
        'RX': lambda self, state: set_absolute_analog(self, Registers.RX, state),
        'RY': lambda self, state: set_absolute_analog(self, Registers.RY, state),
        'LX_REL': set_relative_lx,
        'LY_REL': set_relative_ly,
        'RX_REL': set_relative_rx,
        'RY_REL': set_relative_ry,
        'RESET_ANALOG': lambda self, state: center_analog(self),
    }
