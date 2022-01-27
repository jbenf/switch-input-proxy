import smbus

class Connection():
    def write(self, register: int, data: list):
        pass

class I2CConnector():
    def __init__(self, deviceBus: int):
        self.device = deviceBus
        self.bus = None
        self.initializeBus()
    
    def initializeBus(self):
        self.bus = smbus.SMBus(self.deviceBus)
    
    def write(self, addr: int, register: int, data: list):
        try:
            self.bus.write_i2c_block_data(addr, register, data)
        except IOError:
            print('i2c error', addr)
            self.initializeBus()


class I2CConnection(Connection):
    def __init__(self, address: int, connector: I2CConnector):
        self.address = address
        self.connector = connector
    
    def write(self, register: int, data: list):
        self.connector.write(self.address, register, data)
