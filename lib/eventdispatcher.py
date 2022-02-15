'''This module contains the event dispatching EventDispatcher class'''

from abc import abstractmethod
from datetime import datetime
from lib.common import Event
from lib.config import Configuration, DeviceConfig
from queue import Queue
from lib.relativeinput import RelativeInputHandler

from lib.statemachine import Context, State
from inputs import InputEvent

class DispatcherState(State):
    def __init__(self, output: Queue[Event], config: Configuration):
        self.output = output
        self.config = config

    @abstractmethod
    def handleEvent(self, device: DeviceConfig, event: InputEvent):
        pass

class DispatcherContext(Context[DispatcherState]):
    def handleEvent(self, device: DeviceConfig, event: InputEvent):
        self._state.handleEvent(device, event)

class ProxyState(DispatcherState):
    def handleEvent(self, device: DeviceConfig, event: InputEvent):
        self.output.put(Event(device, event))
        if event.code == self.config.menu.event and event.state == 1 and self.config.menu.device == device:
            self.context.transition_to(MenuState(self.output, self.config))

class MenuState(DispatcherState):
    def handleEvent(self, device: DeviceConfig, event: InputEvent):
        print('menu')
        if event.code == self.config.menu.event and event.state == 0 and self.config.menu.device == device:
            self.output.put(Event(device, event))
            self.context.transition_to(ProxyState(self.output, self.config))



class EventDispatcher:
    '''This class dispatches the events'''
    def __init__(self, configuration: Configuration, outputQueue: Queue[Event]):
        self.output = outputQueue
        self.statemachine = DispatcherContext(ProxyState(outputQueue, configuration))
        self.relativeHandlers = {d: { r.event : RelativeInputHandler(outputQueue, d, r) for r in d.relative } for d in configuration.devices }

    def handleEvent(self, device: DeviceConfig, event: InputEvent, verbose_logging: bool = False):
        if verbose_logging:
            print(datetime.now(), 'SRC: ', device, event.ev_type, event.code, event.state)
        if event.ev_type == 'Absolute' or event.ev_type == 'Key':# or (not analogConfig.RELATIVE and event.ev_type == 'Relative'):
            self.statemachine.handleEvent(device, event)
        elif event.ev_type == 'Relative':
            if len(device.relative) > 0:
                rs = self.relativeHandlers[device]
                handler = rs.get(event.code, None)
                if handler:
                    handler.handleEvent(device, event)
    
    def update(self):
        for r in [ _r for d in self.relativeHandlers.values() for _r in d.values() ]:
            r.update()
