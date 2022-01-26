import smbus

class Connection():
    def write(self, register: int, data: list):
        self.bus.write_i2c_block_data(self.address, register, data)

class I2CConnector():
    def __init__(self, deviceBus: int):
        self.bus = smbus.SMBus(deviceBus)
    
    def write(self, addr: int, register: int, data: list):
        self.bus.write_i2c_block_data(addr, register, data)

class I2CConnection(Connection):
    def __init__(self, address: int, connector: I2CConnector):
        self.address = address
        self.connector = connector
    
    def write(self, register: int, data: list):
        self.bus.write_i2c_block_data(self.address, register, data)
