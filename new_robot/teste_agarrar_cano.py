#!/usr/bin/env python3
import paho.mqtt.client as mqtt
from ev3dev.ev3 import *
from time import sleep
from simple_pid import *

def adjust_claw():

    print("entrei")

    if(left_claw_motor.position > right_claw_motor.position):
        print("left > right")

        while left_claw_motor.position - right_claw_motor.position > -5:
            right_claw_motor.run_forever(speed_sp = 100)
            left_claw_motor.run_forever(speed_sp = -100)
            print(left_claw_motor.position - right_claw_motor.position)


        left_claw_motor.stop()
        right_claw_motor.stop()
        # while 1:
        #     print(left_claw_motor.position, right_claw_motor.position)

    elif (left_claw_motor.position < right_claw_motor.position):
        while - left_claw_motor.position + right_claw_motor.position > -5:
            right_claw_motor.run_forever(speed_sp=-100)
            left_claw_motor.run_forever(speed_sp=100)
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

def verify_this_pipe_is():
    left_claw_motor.run_forever(speed_sp=-500)
    right_claw_motor.run_forever(speed_sp=-500)
    sleep(1.5)
    left_claw_motor.stop()
    right_claw_motor.stop()
    left_claw_motor.position = 0
    right_claw_motor.position = 0

    left_claw_motor.run_forever(speed_sp=100)
    right_claw_motor.run_forever(speed_sp=100)
    sleep(4)

    print("after ", end="")
    print(left_claw_motor.position, right_claw_motor.position)
    print()
    print("sum after ", end="")
    print(left_claw_motor.position + right_claw_motor.position)

    return the_pipe_is()


left_claw_motor = MediumMotor('outC')
right_claw_motor = MediumMotor('outB')
l = LargeMotor("outA")
r = LargeMotor("outD")

right_claw_motor.polarity = "inversed"

left_claw_motor.position = 0
right_claw_motor.position = 0
while 1:
    left_claw_motor.run_forever(speed_sp = -800)
    sleep(1)
    left_claw_motor.stop()
    right_claw_motor.run_forever(speed_sp = -800)
    sleep(1)
    right_claw_motor.stop()

    print("before")
    print(left_claw_motor.position + right_claw_motor.position)

    left_claw_motor.position = 0
    right_claw_motor.position = 0

    strengh = 600
    left_claw_motor.run_to_rel_pos(speed_sp=strengh, position_sp=100)
    left_claw_motor.wait_while('running')
    right_claw_motor.run_to_rel_pos(speed_sp=strengh, position_sp=100)
    right_claw_motor.wait_while('running')
    sleep(1)
    left_claw_motor.position = 0
    right_claw_motor.position = 0

    left_claw_motor.run_forever(speed_sp = 600)
    right_claw_motor.run_forever(speed_sp = 600)
    sleep(2)
    left_claw_motor.stop_action = 'brake'
    right_claw_motor.stop_action = 'brake'
    left_claw_motor.stop()
    right_claw_motor.stop()

    print("after ", end = "")
    print(left_claw_motor.position , right_claw_motor.position)
    print()
    print("sum after ", end = "")
    print(left_claw_motor.position + right_claw_motor.position)
    print(the_pipe_is())
    sleep(5)
