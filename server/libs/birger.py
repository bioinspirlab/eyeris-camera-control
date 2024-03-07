"""@package docstring

Serial port wrapper for interfacing the Birger Canon lens controller with python
"""
import serial
import time

class BirgerControl:
    """
    Open a pyserial object with the given port and baud
    and send/receive commands to the controller with
    some helper functions to streamline common 
    operations.
    """
    def __init__(self, port='/dev/ttyUSB1', baud=115200, timeout=1.0):

        self.port = port
        self.baud = baud
        self.timeout = timeout
        self.zoom = None
        self.focus = None
        self.aperture = None
        self.port_open = False

        try:
            self.device = serial.Serial(
                self.port, self.baud, timeout=self.timeout
            )
            self.port_open = True
            self.device.write(b'mi\r') # move focus to infinity
        except serial.SerialException as e:
            print(e)
            self.port_open = False

    def pretty_print(self):
        print(  'Focus:    ' + str(self.focus) + ' Counts \n' + 
                'Zoom:     ' + str(self.zoom) + ' mm \n' +
                'Aperture: f' + str(self.aperture)
             )

    def print_status(self):
        print(str(self.focus)+','+str(self.zoom)+','+str(self.aperture))

    def read_status(self,max_count=3):
        status = ""
        cr_count = 0
        while cr_count < max_count:
            status = str(self.device.read_until(b'\r'))
            cr_count += 1
        return status

    def get_status(self):

        if self.port_open:
            try:
                self.device.flushInput()
                # zoom and aperture
                self.device.write(b'ls\r')
                status = self.read_status()
                # example: b'@:200mm,f28,28,f320\r0'
                #print(status)
                vals = status.split(':')[1].split(',')
                self.zoom = int(vals[0].split('m')[0])
                self.aperture = float(vals[1].split('f')[1]) / 10.0

                # focus
                self.device.write(b'fd\r')
                status = self.read_status()
                # example: b'fmin:59  fmax:2664  current:2664\r0'
                #print(status)
                vals = status[2:].split(',') # remove the b' 
                self.focus = int(vals[0].split('c')[0])*1000

            except serial.SerialException as e:
                print(e)
            except ValueError as e:
                print(e)

class BirgerEF70200(BirgerControl):
    """
    subclass of BirgerControl specific to the Canon EF 70-200
    zoom lens
    """
    def __init__(self,port='/dev/ttyUSB1', baud=115200, timeout=1.0):
        super().__init__(port,baud,timeout)


"""
Main test code
"""
if __name__=="__main__":

    lc = BirgerEF70200()
    lc.get_status()
    lc.print_status()

