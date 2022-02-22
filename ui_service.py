#!/usr/bin/env python3

from pathlib import Path
from luma.core.virtual import viewport, snapshot
from luma.core.sprite_system import framerate_regulator
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from PIL import ImageFont

from lib.display_connection import DisplayConnectionMessage, DisplayConnectionServer

hello_world = [
    "",
    "Hello World",
    "Mario Kart",
    "Pinball",
    "Super Monkeyball"
]

def make_font(name, size):
    font_path = str(Path(__file__).resolve().parent.joinpath(name))
    return ImageFont.truetype(font_path, size)

def make_snapshot(width, height, text, fonts, color="white"):

    def render(draw, width, height):
        t = text

        for font in fonts:
            size = draw.multiline_textsize(t, font)
            if size[0] > width:
                t = text.replace(" ", "\n")
                size = draw.multiline_textsize(t, font)
            else:
                break

        left = (width - size[0]) // 2
        top = (height - size[1]) // 2
        draw.multiline_text((left, top), text=t, font=font, fill=color,
                            align="center", spacing=-2)

    return snapshot(width, height, render, interval=10)

def fade(current: str, target: str, device, virtual, regulator, fonts, revert: bool):
    if current == target:
        return
    
    widget1 = make_snapshot(device.width, device.height, current, fonts)
    widget2 = make_snapshot(device.width, device.height, target, fonts)

    pos1 = (0,0) if not revert else (0,32)
    pos2 = (0,32) if not revert else (0,0)

    virtual.add_hotspot(widget1, pos1)
    virtual.add_hotspot(widget2, pos2)
    virtual.set_position(pos1)

    steps=8
    
    for i in range(steps):
        with regulator:
            virtual.set_position((0, pos1[1] + (pos2[1]-pos1[1])/steps * i))

    virtual.remove_hotspot(widget1, pos1)
    virtual.remove_hotspot(widget2, pos2)

class TextItem:
    def __init__(self):
        self._value = ''
    
    def value(self):
        return self._value

    def set_value(self, value: str):
        self._value = value

def main():
    serial = i2c(port=1, address=0x3C)
    device = ssd1306(serial, height=32)
    device.contrast(1)
    regulator = framerate_regulator(fps=15)
    fonts = [make_font("code2000.ttf", sz) for sz in range(18, 6, -2)]
    virtual = viewport(device, device.width, device.height*2)

    currentText = TextItem()
    
    connection = DisplayConnectionServer(lambda msg: (
        fade(currentText.value(), msg.payload, device, virtual, regulator, fonts, msg.cmd == 'up'), 
        print(msg.payload), 
        currentText.set_value(msg.payload))
    )

    connection.listen()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
