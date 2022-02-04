import smbus


class Connection():
    def write(self, register: int, data: list):
        pass


class I2CConnector():
    def __init__(self, device_bus: int):
        self.device = device_bus
        self.bus = None
        self.initialize_bus()

    def initialize_bus(self):
        self.bus = smbus.SMBus(self.device)

    def write(self, addr: int, register: int, data: list):
        try:
            self.bus.write_i2c_block_data(addr, register, data)
        except IOError:
            print('i2c error', addr)
            self.initialize_bus()

    def writeByte(self, addr: int, data: int):
        try:
            self.bus.write_byte(addr, data)
        except IOError:
            print('i2c error', addr)
            self.initialize_bus()


class I2CConnection(Connection):
    def __init__(self, address: int, connector: I2CConnector):
        self.address = address
        self.connector = connector

    def write(self, register: int, data: list):
        self.connector.write(self.address, register, data)
