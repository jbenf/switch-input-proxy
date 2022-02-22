from typing import Any

class canvas:
    draw: Any
    image: Any
    device: Any
    dither: Any
    def __init__(self, device, background: Any | None = ..., dither: bool = ...) -> None: ...
    def __enter__(self): ...
    def __exit__(self, type, value, traceback): ...
