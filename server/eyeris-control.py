import logging
import time
import lcm

from threading import Thread
from eyeris import control_status_t, set_zoom_t, set_relays_t, set_light_output_t
from libs.relays import EyeRISRelays
from libs.sensors import EyeRISSensors
from libs.zoom_control import ZoomEF70200
from libs.birger import BirgerEF70200
from libs.dspl import DSPLControl

class LightHandler(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.lights = DSPLControl()
        self.lc = lcm.LCM('udpm://239.255.76.67:7667?ttl=1')
        print('Starting light thread...')
        self.start()
        
    def set_light_output(self, channel, data):
        light_output = set_light_output_t.decode(data)
        lights = ['001','002','003','004','005','006']
        for i,l in enumerate(lights):
            print('Setting light ' + l + " to " + str(light_output.lout[i]))
            self.lights.set_output(light_output.lout[i], l)
            time.sleep(0.1)
        
       
    def run(self):
        self.lc.subscribe('EYERIS_LIGHT_OUTPUT',self.set_light_output)
        while True:
            self.lc.handle()

class ZoomHandler(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.zoom = ZoomEF70200()
        self.lc = lcm.LCM('udpm://239.255.76.67:7667?ttl=1')
        print('Starting zoom thread...')
        self.start()

    def set_zoom(self, channel, data):

        zoom = set_zoom_t.decode(data).focal_length

        print('In Zoom Handler')

        if int(zoom) == 70:
            self.zoom.set_70()
        if int(zoom) == 100:
            self.zoom.set_100()
        if int(zoom) == 135:
            self.zoom.set_135()
        if int(zoom) == 200:
            self.zoom.set_200()

    def run(self):
        self.lc.subscribe('EYERIS_ZOOM',self.set_zoom)
        while True:
            self.lc.handle()

class RelayHandler(Thread):
    
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.relays = EyeRISRelays()
        self.lc = lcm.LCM('udpm://239.255.76.67:7667?ttl=1')
        print('Starting relay thread...')
        self.start()

    def set_relays(self, channel, data):

        relay_msg = set_relays_t.decode(data)
        relay_list = list(relay_msg.relays)
        print(relay_list)
        self.relays.set_relays(EyeRISRelays.all_relays, relay_list)

    def run(self):
        self.lc.subscribe('EYERIS_RELAYS',self.set_relays)
        while True:
            self.lc.handle()

class EyeRISControl:

    def __init__(self):

        self.relays = EyeRISRelays()
        self.sensors = EyeRISSensors()
        self.birger = BirgerEF70200()

        self.zoom_handler = ZoomHandler()
        self.relay_handler = RelayHandler()
        self.light_handler = LightHandler()

        self.lc = lcm.LCM('udpm://239.255.76.67:7667?ttl=1')

    def update_status(self):

        # update sensors and lens info from hardware
        self.sensors.update()
        self.birger.get_status()

        # Create the lcm type to store the message
        status = control_status_t()

        # set the timestamp of the message
        status.timestamp = int(1000000*time.time())

        # populate the message

        # relays
        status.relays = self.relays.get_relays()

        # lens settings
        status.focal_length = self.birger.zoom
        status.focal_distance = self.birger.focus
        status.aperture = self.birger.aperture

        # sensors
        status.temperature = self.sensors.temp
        status.humidity = self.sensors.humidity
        status.pressure = self.sensors.pressure
        status.current = self.sensors.current
        status.power = self.sensors.power
        status.voltage = self.sensors.voltage

        self.lc.publish('EYERIS_CONTROL_STATUS', status.encode())

if __name__=="__main__":

    ec = EyeRISControl()

    while True:
        try:
            ec.update_status()
            time.sleep(0.5)
        except KeyboardInterrupt as e:
            break
            
    print('Finished')