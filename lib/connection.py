"""This module encapsulates a i2c connection"""

from smbus2 import SMBus


class Connection():
    """Interface offering to write data into a register"""

    def write(self, register: int, data: list):
        """write data array into a register"""


class DummyConnection(Connection):
    """Dummy Connection for testing"""
    def __init__(self, name):
        self.name = name

    def write(self, register: int, data: list):
        print(self.name, 'write', hex(register), [hex(d) for d in data])


class I2CConnector():
    """Class encapsulating a i2c bus device"""
    bus: SMBus

    def __init__(self, device_bus: int):
        self.device = device_bus
        self.__initialize_bus()

    def __initialize_bus(self):
        self.bus = SMBus(self.device)

    def write(self, addr: int, register: int, data: list):
        """write data array into a register of a device"""
        try:
            self.bus.write_i2c_block_data(addr, register, data)
        except IOError:
            print('i2c error', addr)
            self.__initialize_bus()

    def write_byte(self, addr: int, data: int):
        """send a single byte to a device"""
        try:
            self.bus.write_byte(addr, data)
        except IOError:
            print('i2c error', addr)
            self.__initialize_bus()


class I2CConnection(Connection):
    """Class encapsulating an i2c connection"""

    def __init__(self, address: int, connector: I2CConnector):
        self.address = address
        self.connector = connector

    def write(self, register: int, data: list):
        self.connector.write(self.address, register, data)
