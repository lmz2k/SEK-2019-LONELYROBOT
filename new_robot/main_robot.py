#!/usr/bin/env python3

import paho.mqtt.client as mqtt
from ev3dev.ev3 import *
from time import sleep
from simple_pid import *

from robot import Robot

bossTaVindo = Robot()

bossTaVindo.claw_init()
bossTaVindo.claw_grab()
bossTaVindo.claw_delivery()

while 1:
    print("SECONDARY")
    print(bossTaVindo.secondary_brick_values())

    print("\nTERTIARY")
    print(bossTaVindo.tertiary_brick_values())

