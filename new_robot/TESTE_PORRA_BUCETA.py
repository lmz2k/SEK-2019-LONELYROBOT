
import paho.mqtt.client as mqtt
from time import sleep
from ev3dev.ev3 import *



claw_motor = LargeMotor('outB')

print("INICIEI")

a = 1000
while True:


    claw_motor.run_forever(speed_sp=a)
    print("claw_motor.state", claw_motor.state, "claw_motor.pos", claw_motor.position)
    sleep(3)
    claw_motor.stop()
    a *= -1

