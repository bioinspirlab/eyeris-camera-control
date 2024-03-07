import smbus2
import bme280
import sys
import board
import adafruit_ina260

class BME280:

    def __init__(self, port=1, address=0x76):
        self.port = port
        self.address = address
        self.bus = smbus2.SMBus(port)
        self.cal = bme280.load_calibration_params(self.bus, self.address)

    def sample(self):
        data = bme280.sample(self.bus, self.address, self.cal)
        return data

    def print_sensor(self, data):
        print(data.id)
        print(data.timestamp)
        print(data.temperature)
        print(data.pressure)
        print(data.humidity)

class INA260:

    def __init__(self, address=0x40):
        self.address = address
        self.i2c = board.I2C()
        self.ina260 = adafruit_ina260.INA260(self.i2c,self.address)

    def sample(self):
        return self.ina260.current, self.ina260.power

    def print_sensor(self, data):
        print(
            "Current: %.2f mA Voltage: %.2f V Power:%.2f mW"
            % (self.ina260.current, self.ina260.voltage, self.ina260.power)
        )

    def get_current(self):
        return self.ina260.current

    def get_power(self):
        return self.ina260.power

    def get_voltage(self):
        return self.ina260.voltage

class EyeRISSensors:

    def __init__(self):

        self.bme280 = []
        self.bme280.append(BME280(address=0x76))
        self.bme280.append(BME280(address=0x77))

        self.ina260 = []
        self.ina260.append(INA260(address=0x40))
        self.ina260.append(INA260(address=0x41))

        self.temp = [0.0,0.0]
        self.humidity = [0.0,0.0]
        self.pressure = [0.0,0.0]
        self.voltage = [0.0,0.0]
        self.current = [0.0,0.0]
        self.power = [0.0,0.0]

    def update(self):

        for i in [0,1]:
            data = self.bme280[i].sample()
            #self.bme280[i].print_sensor(data)
            self.temp[i] = data.temperature
            self.humidity[i] = data.humidity
            self.pressure[i] = data.pressure
        for i in [0,1]:
            data = self.ina260[i].sample()
            #self.ina260[i].print_sensor(data)
            self.current[i] = self.ina260[i].get_current()
            self.power[i] = self.ina260[i].get_power()
            self.voltage[i] = self.ina260[i].get_voltage()

if __name__=="__main__":

    sen = EyeRISSensors()
    sen.update()
