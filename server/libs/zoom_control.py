"""@package docstring

Very simple wrapper around ticcmd for controlling
zoom lens stepper motor. The only trick is using
subprocess to get the output from status calls to ticcmd as
this allows one to update the current position in real-time
in a busy wait loop.

"""
import os
import sys
import yaml
import subprocess
import time

class ZoomControl:

    cmd_name = 'ticcmd'
    safe_start = cmd_name + ' --enter-safe-start'
    resume = cmd_name + ' --resume'
    deenergize = cmd_name + ' --deenergize'
    energize = cmd_name + ' --energize'
    status = cmd_name + ' --status'
    position_threshold = 100

    def __init__(self, settings=None):

        self.settings = settings
        self.pos = None

        if self.settings is not None: 
            cmd = ZoomControl.cmd_name + ' --settings ' + self.settings
            os.system(cmd)

        os.system(ZoomControl.deenergize)

    def ticcmd(self,*args):
        return subprocess.check_output(['ticcmd'] + list(args))

    def get_pos(self):
        status = yaml.load(self.ticcmd('-s', '--full'),Loader=yaml.FullLoader)
        return status['Current position']

    def parse_position(self):
        status = subprocess.getoutput(ZoomControl.status)
        idx = status.find('Current position:')
        try:
            substr = status[idx:]
            pos = substr.split('\n')[0].split(':')[1].lstrip(' ')
            self.pos = int(pos)
            return self.pos
        except:
            return -1

    def set_pos(self, pos):

        # get the current position
        cur_pos = self.get_pos()

        # resume and energize the motor
        self.ticcmd('--exit-safe-start', '--resume', '--position', str(pos))

        # check the current position and compare to target
        while abs(cur_pos - pos) >  ZoomControl.position_threshold:
            cur_pos = self.get_pos()
            time.sleep(0.5)

        # IMPORTANT! deenergize the motor
        self.ticcmd('--deenergize')

class ZoomEF70200(ZoomControl):

    pos_70 = -20000
    pos_100 = -9000
    pos_135 = -3000
    pos_200 = 4000

    def __init__(self, settings=None):
        super().__init__(settings)

    def set_70(self):
        self.set_pos(ZoomEF70200.pos_70)

    def set_100(self):
        print('set 100')
        self.set_pos(ZoomEF70200.pos_100)

    def set_135(self):
        self.set_pos(ZoomEF70200.pos_135)

    def set_200(self):
        self.set_pos(ZoomEF70200.pos_200)

if __name__=="__main__":

    zc = ZoomEF70200()
    zc.set_200()
    time.sleep(0.5)
    zc.set_100()
    time.sleep(0.5)
    zc.set_135()
    time.sleep(0.5)
    zc.set_70()


