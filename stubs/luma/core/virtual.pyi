from luma.core import mixin
from typing import Any

pool: Any

def calc_bounds(xy, entity): ...
def range_overlap(a_min, a_max, b_min, b_max): ...

class viewport(mixin.capabilities):
    segment_mapper: Any
    def __init__(self, device, width, height, mode: Any | None = ..., dither: bool = ...) -> None: ...
    def display(self, image) -> None: ...
    def set_position(self, xy) -> None: ...
    def add_hotspot(self, hotspot, xy) -> None: ...
    def remove_hotspot(self, hotspot, xy) -> None: ...
    def is_overlapping_viewport(self, hotspot, xy): ...
    def refresh(self) -> None: ...

class hotspot(mixin.capabilities):
    def __init__(self, width, height, draw_fn: Any | None = ...) -> None: ...
    def paste_into(self, image, xy) -> None: ...
    def should_redraw(self): ...
    def update(self, draw) -> None: ...

class snapshot(hotspot):
    interval: Any
    last_updated: Any
    def __init__(self, width, height, draw_fn: Any | None = ..., interval: float = ...) -> None: ...
    def should_redraw(self): ...
    def paste_into(self, image, xy) -> None: ...

class terminal:
    font: Any
    default_fgcolor: Any
    default_bgcolor: Any
    animate: Any
    tabstop: Any
    word_wrap: Any
    width: Any
    height: Any
    size: Any
    tw: Any
    def __init__(self, device, font: Any | None = ..., color: str = ..., bgcolor: str = ..., tabstop: int = ..., line_height: Any | None = ..., animate: bool = ..., word_wrap: bool = ...) -> None: ...
    def clear(self) -> None: ...
    def println(self, text: str = ...) -> None: ...
    def puts(self, text) -> None: ...
    def putch(self, char) -> None: ...
    def carriage_return(self) -> None: ...
    def tab(self) -> None: ...
    def newline(self) -> None: ...
    def backspace(self) -> None: ...
    def erase(self) -> None: ...
    def flush(self) -> None: ...
    def foreground_color(self, value) -> None: ...
    def background_color(self, value) -> None: ...
    def reset(self) -> None: ...
    def reverse_colors(self) -> None: ...

class history(mixin.capabilities):
    segment_mapper: Any
    def __init__(self, device) -> None: ...
    def display(self, image) -> None: ...
    def savepoint(self) -> None: ...
    def restore(self, drop: int = ...) -> None: ...
    def __len__(self): ...

class sevensegment:
    device: Any
    undefined: Any
    segment_mapper: Any
    def __init__(self, device, undefined: str = ..., segment_mapper: Any | None = ...) -> None: ...
    @property
    def text(self): ...
    @text.setter
    def text(self, value) -> None: ...

class character:
    device: Any
    font: Any
    def __init__(self, device, font: Any | None = ..., undefined: str = ...) -> None: ...
    @property
    def text(self): ...
    @text.setter
    def text(self, value) -> None: ...
