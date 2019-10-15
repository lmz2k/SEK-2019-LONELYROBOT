
import paho.mqtt.client as mqtt
from time import sleep
from ev3dev.ev3 import *



claw_motor = LargeMotor()



print("INICIEI")
claw_motor.reset()


claw_motor.run_forever(speed_sp=-1000)
sleep(5)
claw_motor.stop()

