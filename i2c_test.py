import smbus

DEVICE_BUS = 1
DEVICE_ADDR = 0x52
bus = smbus.SMBus(DEVICE_BUS)
bus.write_i2c_block_data(DEVICE_ADDR, 0x01, [0x04])