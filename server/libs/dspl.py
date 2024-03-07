"""@package docstring

Serial port wrapper for interfacing the DSPL Lights with python
"""
import serial
import time

class DSPLControl:
    """
    Open a pyserial object with the given port and baud
    and send/receive commands to the light(s) with
    some helper functions to streamline common 
    operations.
    """
    def __init__(self, port='/dev/ttyUSB0', baud=9600, timeout=1.0):

        self.port = port
        self.baud = baud
        self.timeout = timeout
        self.port_open = False

        try:
            self.device = serial.Serial(
                self.port, self.baud, timeout=self.timeout
            )
            self.port_open = True
        except serial.SerialException as e:
            print(e)
            self.port_open = False


    def set_output(self, output_level, dev='001'):
        cmd = '!' + dev + ':lout=' + str(int(output_level)) + '\r\n'
        self.device.write(cmd.encode())

