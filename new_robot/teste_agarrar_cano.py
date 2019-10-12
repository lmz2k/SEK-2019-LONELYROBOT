#!/usr/bin/env python3
import paho.mqtt.client as mqtt
from ev3dev.ev3 import *
from time import sleep
from simple_pid import *

def adjust_claw():

    print("entrei")

    sleep(2)


    if(left_claw_motor.position > right_claw_motor.position):
        print("left > right")
        sleep(2)
        while left_claw_motor.position - right_claw_motor.position > -10:
            right_claw_motor.run_forever(speed_sp = 10)
            left_claw_motor.run_forever(speed_sp = -10)
            print(left_claw_motor.position - right_claw_motor.position)


        left_claw_motor.stop()
        right_claw_motor.stop()
        # while 1:
        #     print(left_claw_motor.position, right_claw_motor.position)

    elif (left_claw_motor.position < right_claw_motor.position):
        while - left_claw_motor.position + right_claw_motor.position > -10:
            right_claw_motor.run_forever(speed_sp=-10)
            left_claw_motor.run_forever(speed_sp=10)
            print(left_claw_motor.position - right_claw_motor.position)

        left_claw_motor.stop()
        right_claw_motor.stop()
        # while 1:
        #     print(left_claw_motor.position, right_claw_motor.position)


def the_pipe_is():
    sum = (left_claw_motor.position + right_claw_motor.position)

    if(sum > 385):
        return "lost"

    elif(sum > 345):
        return "perpendicular"

    return "parallel"



left_claw_motor = MediumMotor('outC')
right_claw_motor = MediumMotor('outB')
l = LargeMotor("outA")
r = LargeMotor("outD")

# right_claw_motor.polarity = "inversed"

left_claw_motor.position = 0
right_claw_motor.position = 0

left_claw_motor.run_forever(speed_sp = -100)
right_claw_motor.run_forever(speed_sp = -100)
sleep(3)
left_claw_motor.stop()
right_claw_motor.stop()

print("before")
print(left_claw_motor.position + right_claw_motor.position)

left_claw_motor.position = 0
right_claw_motor.position = 0

left_claw_motor.run_forever(speed_sp = 200)
right_claw_motor.run_forever(speed_sp = 200)
sleep(3)

print("after ", end = "")
print(left_claw_motor.position , right_claw_motor.position)
print()
print("sum after ", end = "")
print(left_claw_motor.position + right_claw_motor.position)

print(the_pipe_is())

adjust_claw()

left_claw_motor.run_forever(speed_sp = -100)
right_claw_motor.run_forever(speed_sp = -100)
sleep(3)
left_claw_motor.stop()
right_claw_motor.stop()

l.run_forever(speed_sp = 200)
r.run_forever(speed_sp = 200)
sleep(1)
l.stop()
r.stop()
while 1:
    print(left_claw_motor.position, right_claw_motor.position)

