"""This module encapsulates a i2c connection"""

import smbus

"""Interface offering to write data into a register"""
class Connection():
    """write data array into a register"""
    def write(self, register: int, data: list):
        pass

"""Class encapsulating a i2c bus device"""
class I2CConnector(Connection):
    def __init__(self, device_bus: int):
        self.device = device_bus
        self.bus = None
        self.__initialize_bus()

    def __initialize_bus(self):
        self.bus = smbus.SMBus(self.device)

    """write data array into a register of a device"""
    def write(self, addr: int, register: int, data: list):
        try:
            self.bus.write_i2c_block_data(addr, register, data)
        except IOError:
            print('i2c error', addr)
            self.__initialize_bus()

    """send a single byte to a device"""
    def write_byte(self, addr: int, data: int):
        try:
            self.bus.write_byte(addr, data)
        except IOError:
            print('i2c error', addr)
            self.__initialize_bus()


"""Class encapsulating an i2c connection"""
class I2CConnection(Connection):
    def __init__(self, address: int, connector: I2CConnector):
        self.address = address
        self.connector = connector

    """override
    def write(self, register: int, data: list):
        self.connector.write(self.address, register, data)
