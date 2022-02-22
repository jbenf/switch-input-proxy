from typing import Callable, Dict, List
import yaml

INVALID = -999

class BindingConfig:
    def __init__(self, data: dict):
        self.event = data['event']
        self.state = data.get('state', INVALID)
        self.invoke = data['invoke']
        self.address = data.get('address', INVALID)

class DeviceConfig:
    def __init__(self, data: dict):
        self.name = data['name']
        self.index = data.get('index', 0)
        self.bindings = [BindingConfig(d) for d in data['bindings']]
        self.relative = [RelativeConfig(d) for d in data.get('relative', [])]
        self.mappings: Dict[str, List[BindingConfig]] = {}
        for b in self.bindings:
            bs = self.mappings.get(b.event, [])
            bs.append(b)
            self.mappings[b.event] = bs
    
    def __str__(self):
        return 'DeviceConfig ' + self.name + '#' + str(self.index)
    
    def __key(self):
        return (self.name, self.index)

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, DeviceConfig):
            return self.__key() == other.__key()
        return False


class RelativeConfig:
    def __init__(self, data: dict):
        self.event: str = data['event']
        self.invoke: str = data['invoke']
        self.mult: float = data.get('mult', 1.0)

class MenuConfig:
    def __init__(self, data: dict):
        self.event = data['event']
        self.device = DeviceConfig(data['device'])


class Configuration:
    def __init__(self, data: dict):
        self.name = data['name']
        self.i2c_device = data['i2c_device']
        self.category = data.get('category', 'Default')
        self.devices = [DeviceConfig(d) for d in data['devices']]
        self.addresses = list(set([b.address for d in self.devices for b in d.bindings]))
        self.menu = MenuConfig(data['menu'])


    @staticmethod
    def load(base_config_path: str, config_path: str):
        base = {}

        if base_config_path != None:
            with open(base_config_path, "r") as stream:
                base = yaml.safe_load(stream)

        with open(config_path, "r") as stream:
            config = yaml.safe_load(stream)
            merged = base | config

            return Configuration(merged)

class ConfigurationProvider:
    listeners: List[Callable[[Configuration], None]] = []

    def __init__(self, initial_config: Configuration):
        self.current_config = initial_config
    
    def register_config_listener(self, listener: Callable[[Configuration], None]):
        self.listeners.append(listener)
        listener(self.current_config)
    
    def change_config(self, new_config: Configuration):
        self.current_config = new_config
        for l in self.listeners:
            l(new_config)