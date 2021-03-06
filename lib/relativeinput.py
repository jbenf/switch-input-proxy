from queue import Queue
from lib.common import Event
from lib.config import DeviceConfig, RelativeConfig
from inputs import InputEvent


class RelativeInputHandler:
    def __init__(self, output: Queue[Event], device: DeviceConfig, relative: RelativeConfig):
        self.abs: float = 128.0
        self.buffer: Queue[Event] = Queue()
        self.output = output
        self.relative = relative
        self.active: bool = False
        self.device = device
    
    def handleEvent(self, device: DeviceConfig, event: InputEvent):
        self.buffer.put(Event(device, event))

    def update(self):
        self.abs = (2*self.abs+128)/3

        self.active |= not self.buffer.empty()

        while not self.buffer.empty():
            ev = self.buffer.get_nowait()

            self.abs += ev.payload.state

        if self.active:
            value = self.value()
            event_info = {
                "ev_type": "Absolute",
                "state": value,
                "timestamp": 0,
                "code": self.relative.invoke
            }
            self.output.put(Event(self.device, InputEvent(self.device, event_info)))
            self.active = value != 128
    
    def value(self) -> int:
        return min(255, max(0, int(round(self.abs))))

