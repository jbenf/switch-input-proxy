from typing import Any

class ComposableImage:
    def __init__(self, image, position=..., offset=...) -> None: ...
    @property
    def position(self): ...
    @position.setter
    def position(self, value) -> None: ...
    @property
    def offset(self): ...
    @offset.setter
    def offset(self, value) -> None: ...
    @property
    def width(self): ...
    @property
    def height(self): ...
    def image(self, size): ...

class ImageComposition:
    composed_images: Any
    def __init__(self, device) -> None: ...
    def add_image(self, image) -> None: ...
    def remove_image(self, image) -> None: ...
    def __call__(self): ...
    def refresh(self) -> None: ...
