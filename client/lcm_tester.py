
import lcm


def handler(data, channel):
    print("Received: " + channel)

lc = lcm.LCM('udpm://239.255.76.67:7667?ttl=0')
lc.subscribe('EYERIS_RELAYS', handler)
lc.subscribe('EYERIS_LIGHT_OUTPUT', handler)

while True:
    lc.handle()