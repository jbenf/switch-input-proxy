'''This module contains the event dispatching EventDispatcher class'''

from abc import abstractmethod
from datetime import datetime
from threading import Lock
from typing import Callable, Dict
from lib.common import Event
from lib.config import INVALID, Configuration, ConfigurationProvider, DeviceConfig
from queue import Queue
from lib.relativeinput import RelativeInputHandler

from lib.statemachine import Context, State
from inputs import InputEvent

class DispatcherState(State):
    def __init__(self, output: Queue[Event], config: Configuration, menu_listener: Callable[[str], None]):
        self.output = output
        self.config = config
        self.menu_listener = menu_listener

    @abstractmethod
    def handleEvent(self, device: DeviceConfig, event: InputEvent):
        pass

class DispatcherContext(Context[DispatcherState]):
    def handleEvent(self, device: DeviceConfig, event: InputEvent):
        self._state.handleEvent(device, event)
    
    def getState(self):
        return self._state

class ProxyState(DispatcherState):
    def handleEvent(self, device: DeviceConfig, event: InputEvent):
        self.output.put(Event(device, event))
        if event.code == self.config.menu.event and event.state == 1 and self.config.menu.device == device:
            self.context.transition_to(MenuState(self.output, self.config, self.menu_listener))

class MenuState(DispatcherState):
    def handleEvent(self, device: DeviceConfig, event: InputEvent):
        for b in self.config.menu.device.mappings.get(event.code, []):
            if b.state == INVALID or b.state == event.state:
                print('invoking menu event: ', b.invoke)
                self.menu_listener(b.invoke)
        if event.code == self.config.menu.event and event.state == 0 and self.config.menu.device == device:
            self.output.put(Event(device, event))
            self.context.transition_to(ProxyState(self.output, self.config, self.menu_listener))



class EventDispatcher:
    '''This class dispatches the events'''

    def __init__(self, config: ConfigurationProvider, outputQueue: Queue[Event]):
        self.output = outputQueue
        self.lock = Lock()
        self.menu_listeners: Dict[str, Callable[[], None]] = {}
        self.statemachine = DispatcherContext(ProxyState(self.output, config.current_config, self.on_menu_event))
        config.register_config_listener(self.update_config)
    
    def register_menu_listener(self, cmd: str, listener: Callable[[], None]):
        self.menu_listeners[cmd] = listener
    
    def on_menu_event(self, cmd: str):
        l = self.menu_listeners.get(cmd, None)
        if l:
            l()

    def update_config(self, new_config: Configuration):
        print('Updating config: ', new_config.name)
        state = self.statemachine.getState()
        if isinstance(state, ProxyState):
            state = ProxyState(self.output, new_config, self.on_menu_event)
        else:
            state = MenuState(self.output, new_config, self.on_menu_event)
        self.statemachine = DispatcherContext(state)
        self.lock.acquire()
        self.relativeHandlers = {d: { r.event : RelativeInputHandler(self.output, d, r) for r in d.relative } for d in new_config.devices }
        self.lock.release()

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
        self.lock.acquire()
        for r in [ _r for d in self.relativeHandlers.values() for _r in d.values() ]:
            r.update()
        self.lock.release()
