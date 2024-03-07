from eyeris import control_status_t
import lcm
import numpy as np
import sys
import time


if __name__=="__main__":

    if sys.argv[1] == 'send':
        status = control_status_t()

        lc = lcm.LCM('udpm://239.255.76.67:7667?ttl=1')

        while True:

            status.timestamp = int(1000000 * time.time())
            status.aperture = 2.8
            status.focal_distance = 500
            status.focal_length = 140
            status.temperature = 25 + 3 * np.random.random(2)
            status.humidity = 55 + 3 * np.random.random(2)
            status.pressure = 101000 + 30 * np.random.random(2)

            lc.publish('EYERIS_CONTROL_STATUS', status.encode())

            time.sleep(0.5)

    elif sys.argv[1] == 'receive':

        def handler(channel, data):
            status = control_status_t.decode(data)
            print(status.timestamp)

        lc = lcm.LCM()
        lc.subscribe('EYERIS_CONTROL_STATUS', handler)

        lc.handle()
