#!/usr/bin/env python3

import paho.mqtt.client as mqtt
from ev3dev.ev3 import *
from time import sleep
from simple_pid import *

left_wheel_motor = LargeMotor('outA')
right_wheel_motor = LargeMotor('outD')

left_claw_motor = LargeMotor('outC')
right_claw_motor = LargeMotor('outB')

