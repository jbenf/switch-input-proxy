from luma.core.const import common
from typing import Any

class ssd1306(common):
    CHARGEPUMP: int
    COLUMNADDR: int
    COMSCANDEC: int
    COMSCANINC: int
    EXTERNALVCC: int
    MEMORYMODE: int
    PAGEADDR: int
    SETCOMPINS: int
    SETDISPLAYCLOCKDIV: int
    SETDISPLAYOFFSET: int
    SETHIGHCOLUMN: int
    SETLOWCOLUMN: int
    SETPRECHARGE: int
    SETSEGMENTREMAP: int
    SETSTARTLINE: int
    SETVCOMDETECT: int
    SWITCHCAPVCC: int
sh1106 = ssd1306

class ssd1322(common):
    DISPLAYON: int
    DISPLAYOFF: int
    SETCONTRAST: int

class ssd1362(common):
    DISPLAYON: int
    DISPLAYOFF: int
    SETCONTRAST: int

class ws0010:
    CLEAR: int
    HOME: int
    ENTRY: int
    DISPLAYOFF: int
    DISPLAYON: int
    POWEROFF: int
    POWERON: int
    GRAPHIC: int
    CHAR: int
    FUNCTIONSET: int
    DL8: int
    DL4: int
    DDRAMADDR: int
    CGRAMADDR: int
    FONTDATA: Any

class winstar_weh(ws0010):
    FONTDATA: Any
