import abc
from luma.core.device import device
from luma.oled.device.framebuffer_mixin import __framebuffer_mixin
from typing import Any

class greyscale_device(device, __framebuffer_mixin, metaclass=abc.ABCMeta):
    __metaclass__: Any
    def __init__(self, const, serial_interface, width, height, rotate, mode, framebuffer, nibble_order, **kwargs) -> None: ...
    def display(self, image) -> None: ...
