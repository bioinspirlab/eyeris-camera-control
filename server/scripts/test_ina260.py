import time
import board
import adafruit_ina260
 
i2c = board.I2C()
ina260 = adafruit_ina260.INA260(i2c,address=0x41)
while True:
    print(
        "Current: %.2f mA Voltage: %.2f V Power:%.2f mW"
        % (ina260.current, ina260.voltage, ina260.power)
    )
    time.sleep(1)
