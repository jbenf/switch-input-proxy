from typing import Any

class proportional:
    font: Any
    def __init__(self, font) -> None: ...
    def __getitem__(self, ascii_code): ...

class tolerant:
    font: Any
    missing_code: Any
    def __init__(self, font, missing: str = ...) -> None: ...
    def __getitem__(self, ascii_code): ...

CP437_FONT: Any
SINCLAIR_FONT: Any
LCD_FONT: Any
UKR_FONT: Any
TINY_FONT: Any
SEG7_FONT: Any
SPECCY_FONT: Any
ATARI_FONT: Any
DEFAULT_FONT = CP437_FONT
