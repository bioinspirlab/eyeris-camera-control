from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero import LED

class Relays:

    def __init__(self, pins=[], active_high=False):

        self.relays = []
        self.pins = pins
        self.active_high = active_high
        for p in self.pins:
            self.relays.append(
                LED(p, 
                    active_high=self.active_high,
                    initial_value=False, 
                    pin_factory=PiGPIOFactory())
                )

    def set(self, num, state):

        if num >= 0 and num < len(self.relays):
            if state:
                self.relays[num].on()
            else:
                self.relays[num].off()

    def get(self, num):

        if num >= 0 and num < len(self.relays):

            return self.relays[num].is_lit

class EyeRISRelays:

    all_relays = [0,1,2,3]
    cam_relays = [0]
    light_relays = [2,3]


    def __init__(self):

        self.relays = Relays(pins=[4, 17, 27, 22], active_high=False)

    def set_relays(self, relay_list, state_list):
        for ind, l in enumerate(relay_list):
            self.relays.set(l, state_list[ind])

    def camera_on(self):
        self.set_relays(EyeRISRelays.cam_relays, True)

    def camera_off(self):
        self.set_relays(EyeRISRelays.cam_relays, False)

    def lights_on(self):
        self.set_relays(EyeRISRelays.light_relays, True)

    def lights_off(self):
        self.set_relays(EyeRISRelays.light_relays, False)

    def get_relays(self):
        status = []
        for r in EyeRISRelays.all_relays:
            status.append(self.relays.get(r))
        return status


if __name__=="__main__":

    import time

    relays = Relays(pins=[4, 17, 27, 22], active_high=False)

    for i in range(0,4):
        if relays.get(i):
            print('Relay ' + str(i) + ' is ON, turning OFF')
            relays.set(i,False)
        else:
            print('Relay ' + str(i) + ' is OFF, turning ON')
            relays.set(i,True)

        time.sleep(1.0)



