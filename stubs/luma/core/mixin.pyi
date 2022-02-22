from typing import Any

class capabilities:
    width: int
    height: int
    size: Any
    bounding_box: Any
    rotate: Any
    mode: Any
    persist: bool
    def capabilities(self, width, height, rotate, mode: str = ...) -> None: ...
    def clear(self) -> None: ...
    def preprocess(self, image): ...
    def display(self, image) -> None: ...
