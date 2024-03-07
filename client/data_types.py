import time

class DataType:

    def __init__(self):
        self.type = 'DataType'
    def write_header(self, f):
        pass
    def write_data(self, f, data):
        pass


class EyeRISDataType(DataType):


    def __init__(self, delim=','):
        self.delim = delim
        self.type = 'EyeRISDataType'

    def write_header(self, f):
        header = ['Timestamp', 'Temp1', 'Temp2', 'Humidity1', 'Humidity2', 'Pressure1', 'Pressure2',
                  'Power1', 'Power2', 'Current1', 'Current2', 'Focus', 'Zoom', 'Iris', 'Relay1', 'Relay2', 'Relay3',
                  'Relay4']
        f.write(self.delim.join(header)+'\n')

    def write_data(self, f, data):

        # use system time rather than control board time
        # The system time will have the same clock as the camera frame grabber while
        # the raspi may or may not be synched with the system clock

        f.write(str(int(1000000*time.time())) + self.delim)
        f.write(str(data.temperature[0]) + self.delim)
        f.write(str(data.temperature[1]) + self.delim)
        f.write(str(data.humidity[0]) + self.delim)
        f.write(str(data.humidity[1]) + self.delim)
        f.write(str(data.pressure[0]) + self.delim)
        f.write(str(data.pressure[1]) + self.delim)
        f.write(str(data.power[0] / 1000.0) + self.delim)
        f.write(str(data.power[1] / 1000.0) + self.delim)
        f.write(str(data.current[0] / 1000.0) + self.delim)
        f.write(str(data.current[1] / 1000.0) + self.delim)
        f.write(str(data.focal_distance) + self.delim)
        f.write(str(data.focal_length) + self.delim)
        f.write(str(data.aperture) + self.delim)
        relay_list = list(data.relays)
        for i in range(0, 4):
            f.write(str(relay_list[i]) + self.delim)

        f.write('\n')
