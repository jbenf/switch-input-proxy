from typing import NamedTuple
from lib.connection import Connection

class Btn_0_Bits(NamedTuple):
    MINUS   = 2**0
    PLUS    = 2**1
    LCLICK  = 2**2
    RCLICK  = 2**3
    HOME    = 2**4
    CAPTURE = 2**5


class Btn_1_Bits(NamedTuple):
    Y  = 2**0
    B  = 2**1
    A  = 2**2
    X  = 2**3
    L  = 2**4
    R  = 2**5
    ZL = 2**6
    ZR = 2**7


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


class Gamepad():
    bitmap_BTN_0 = 0x0    # Buttons such as Minus, Home and Capture
    bitmap_BTN_1 = 0x0    # Buttons such as A, B, X, Y
    bitmap_HAT   = 0x08
    bitmap_LX    = 0x80
    bitmap_LY    = 0x80
    bitmap_RX    = 0x80
    bitmap_RY    = 0x80

    def __init__(self, connection: Connection):
        self.connection = connection
    
