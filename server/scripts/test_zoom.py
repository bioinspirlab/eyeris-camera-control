import time
import sys
import random

sys.path.append('..')

from libs.zoom_control import ZoomEF70200
from libs.birger import BirgerEF70200

if __name__=="__main__":

    print('Testing Zoom lens functions...')
    print('Ctrl-C to exit.')

    zc = ZoomEF70200()
    lc = BirgerEF70200()

    zc.set_pos(0)

    positions = range(-20000,4000,1000)

    while True:

        p = random.choice(positions)

        zc.set_pos(p)
        lc.get_status()
        print('Position: ' + "{:05d}".format(p) +
                ',\tLens focal length: ' + "{:03d}".format(lc.zoom))
        time.sleep(5)


