from re import VERBOSE
from typing import NamedTuple
from lib.connection import Connection


class Registers(NamedTuple):
    BTN_0 = 0x0
    BTN_1 = 0x1
    HAT   = 0x2
    LX    = 0x3
    LY    = 0x4
    RX    = 0x5
    RY    = 0x6

class btn_0_mask(NamedTuple):
    MINUS   = 2**0
    PLUS    = 2**1
    LCLICK  = 2**2
    RCLICK  = 2**3
    HOME    = 2**4
    CAPTURE = 2**5

class btn_1_mask(NamedTuple):
    Y  = 2**0
    B  = 2**1
    A  = 2**2
    X  = 2**3
    L  = 2**4
    R  = 2**5
    ZL = 2**6
    ZR = 2**7


class hat_mask(NamedTuple):
    DPAD_UP    = 2**0
    DPAD_RIGHT = 2**1
    DPAD_DOWN  = 2**2
    DPAD_LEFT  = 2**3

class hat_values(NamedTuple):
    UP         = 0x00
    UP_RIGHT   = 0x01
    RIGHT      = 0x02
    DOWN_RIGHT = 0x03
    DOWN       = 0x04
    DOWN_LEFT  = 0x05
    LEFT       = 0x06
    UP_LEFT    = 0x07
    CENTER     = 0x08

hat_map = {
    hat_mask.DPAD_UP: hat_values.UP,
    hat_mask.DPAD_UP | hat_mask.DPAD_RIGHT: hat_values.UP_RIGHT,
    hat_mask.DPAD_RIGHT: hat_values.RIGHT,
    hat_mask.DPAD_DOWN | hat_mask.DPAD_RIGHT: hat_values.DOWN_RIGHT,
    hat_mask.DPAD_DOWN: hat_values.DOWN,
    hat_mask.DPAD_DOWN | hat_mask.DPAD_LEFT: hat_values.DOWN_LEFT,
    hat_mask.DPAD_LEFT: hat_values.LEFT,
    hat_mask.DPAD_UP | hat_mask.DPAD_LEFT: hat_values.UP_LEFT,
}

class analog_values(NamedTuple):
    CENTER     = 0x80

def handleBtn0(self, mask: int, state: int):
    if state == 1:
        self.bitmap_BTN_0 = self.bitmap_BTN_0 | mask
    else:
        self.bitmap_BTN_0 = self.bitmap_BTN_0 & ~ mask
    
    self.connection.write(Registers.BTN_0, [self.bitmap_BTN_0])

def handleBtn1(self, mask: int, state: int):
    if state == 1:
        self.bitmap_BTN_1 = self.bitmap_BTN_1 | mask
    else:
        self.bitmap_BTN_1 = self.bitmap_BTN_1 & ~ mask
    
    self.connection.write(Registers.BTN_1, [self.bitmap_BTN_1])

def handleHat(self, mask: int, state: int):
    if state == 1:
        self.bitmap_HAT = self.bitmap_HAT | mask
    else:
        self.bitmap_HAT = self.bitmap_HAT & ~mask
    
    bitmap = hat_map.get(self.bitmap_HAT, hat_values.CENTER)

    if bitmap == hat_values.CENTER:
        self.bitmap_HAT = 0

    self.connection.write(Registers.HAT, [bitmap])
    

class Gamepad():
    bitmap_BTN_0 = 0x00    # Buttons such as Minus, Home and Capture
    bitmap_BTN_1 = 0x00    # Buttons such as A, B, X, Y
    bitmap_HAT   = 0x00
    bitmap_LX    = analog_values.CENTER
    bitmap_LY    = analog_values.CENTER
    bitmap_RX    = analog_values.CENTER
    bitmap_RY    = analog_values.CENTER

    

    def __init__(self, connection: Connection):
        self.connection = connection

    def event(self, invoke: str, state: int):
        print(invoke, state)
        func = self.handling.get(invoke, None)
        if func != None:
            func(self, state)
        else:
            print('Unkown Event: ', invoke)
    
    handling = {
        'A': lambda self, state: handleBtn1(self, btn_1_mask.A, state),
        'B': lambda self, state: handleBtn1(self, btn_1_mask.B, state),
        'X': lambda self, state: handleBtn1(self, btn_1_mask.X, state),
        'Y': lambda self, state: handleBtn1(self, btn_1_mask.Y, state),
        'L': lambda self, state: handleBtn1(self, btn_1_mask.L, state),
        'R': lambda self, state: handleBtn1(self, btn_1_mask.R, state),
        'ZL': lambda self, state: handleBtn1(self, btn_1_mask.ZL, state),
        'ZR': lambda self, state: handleBtn1(self, btn_1_mask.ZR, state),
        'MINUS': lambda self, state: handleBtn0(self, btn_0_mask.MINUS, state),
        'PLUS': lambda self, state: handleBtn0(self, btn_0_mask.PLUS, state),
        'HOME': lambda self, state: handleBtn0(self, btn_0_mask.HOME, state),
        'LCLICK': lambda self, state: handleBtn0(self, btn_0_mask.LCLICK, state),
        'RCLICK': lambda self, state: handleBtn0(self, btn_0_mask.RCLICK, state),
        'CAPTURE': lambda self, state: handleBtn0(self, btn_0_mask.CAPTURE, state),
        'DPAD_UP': lambda self, state: handleHat(self, hat_mask.DPAD_UP, state),
        'DPAD_RIGHT': lambda self, state: handleHat(self, hat_mask.DPAD_RIGHT, state),
        'DPAD_DOWN': lambda self, state: handleHat(self, hat_mask.DPAD_DOWN, state),
        'DPAD_LEFT': lambda self, state: handleHat(self, hat_mask.DPAD_LEFT, state),
    }
    