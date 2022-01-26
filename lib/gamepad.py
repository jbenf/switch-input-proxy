from re import VERBOSE
from typing import NamedTuple
from lib.connection import Connection

REGISTERS = {
    'BTN_0' : 0x0,
    'BTN_1' : 0x1,
    'HAT'   : 0x2,
    'LX'    : 0x3,
    'LY'    : 0x4,
    'RX'    : 0x5,
    'RY'    : 0x6,
}

class Registers(NamedTuple):
    BTN_0 = 0x0
    BTN_1 = 0x1
    HAT   = 0x2
    LX    = 0x3
    LY    = 0x4
    RX    = 0x5
    RY    = 0x6

BTN_O_MASK = {
    'MINUS'  : 2**0,
    'PLUS'   : 2**1,
    'LCLICK' : 2**2,
    'RCLICK' : 2**3,
    'HOME'   : 2**4,
    'CAPTURE': 2**5,
}

class Btn_0_mask(NamedTuple):
    MINUS   = 2**0
    PLUS    = 2**1
    LCLICK  = 2**2
    RCLICK  = 2**3
    HOME    = 2**4
    CAPTURE = 2**5

BTN_1_MASK = {
    'Y' : 2**0,
    'B' : 2**1,
    'A' : 2**2,
    'X' : 2**3,
    'L' : 2**4,
    'R' : 2**5,
    'ZL': 2**6,
    'ZR': 2**7,
}

class btn_1_mask(NamedTuple):
    Y  = 2**0
    B  = 2**1
    A  = 2**2
    X  = 2**3
    L  = 2**4
    R  = 2**5
    ZL = 2**6
    ZR = 2**7

HAT_VALUES = {
    'UP'         : 0x00,
    'UP_RIGHT'   : 0x01,
    'RIGHT'      : 0x02,
    'DOWN_RIGHT' : 0x03,
    'DOWN'       : 0x04,
    'DOWN_LEFT'  : 0x05,
    'LEFT'       : 0x06,
    'UP_LEFT'    : 0x07,
    'CENTER'     : 0x08,
}

class Hat_Values(NamedTuple):
    UP         = 0x00
    UP_RIGHT   = 0x01
    RIGHT      = 0x02
    DOWN_RIGHT = 0x03
    DOWN       = 0x04
    DOWN_LEFT  = 0x05
    LEFT       = 0x06
    UP_LEFT    = 0x07
    CENTER     = 0x08

class Analog_Values(NamedTuple):
    CENTER     = 0x80

def handleBtn1(self, mask: int, state: int):
    if state == 1:
        self.bitmap_BTN_1 = self.bitmap_BTN_1 | mask
    else:
        self.bitmap_BTN_1 = self.bitmap_BTN_1 ^ mask
    
    self.connection.write(Registers.BTN_1, [self.bitmap_BTN_1])
    

class Gamepad():
    bitmap_BTN_0 = 0x00    # Buttons such as Minus, Home and Capture
    bitmap_BTN_1 = 0x00    # Buttons such as A, B, X, Y
    bitmap_HAT   = Hat_Values.CENTER
    bitmap_LX    = Analog_Values.CENTER
    bitmap_LY    = Analog_Values.CENTER
    bitmap_RX    = Analog_Values.CENTER
    bitmap_RY    = Analog_Values.CENTER

    

    def __init__(self, connection: Connection):
        self.connection = connection

    def event(self, invoke: str, state: int):
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
    }
    
