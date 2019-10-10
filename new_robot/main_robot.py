#!/usr/bin/env python3

import paho.mqtt.client as mqtt
from ev3dev.ev3 import *
from time import sleep
from simple_pid import *

from robot import Robot

bossTaVindo = Robot()

# bossTaVindo.claw_init()
# bossTaVindo.claw_grab()
# bossTaVindo.claw_delivery()

bossTaVindo.change_color_mode("COL-COLOR")

# bossTaVindo.color_alignment("black", bossTaVindo.PIPE_AREA, ["white"])
# bossTaVindo.rotate_right_90()
# bossTaVindo.stop_wheel()
# bossTaVindo.left_pid(80000)

try:
    # while 1:
    #     # print("SECONDARY")
    #     # print(bossTaVindo.secondary_brick_values())
    #     #
    #     # print("\nTERTIARY")
    #     # print(bossTaVindo.tertiary_brick_values())
    #     print(bossTaVindo.gyro.value())
    while not (bossTaVindo.search_left_border()):
        bossTaVindo.move_motors(400,400)
    bossTaVindo.stop_wheel()
    bossTaVindo.move_motors(-200,-200)
    sleep(0.5)
    bossTaVindo.stop_wheel()
    bossTaVindo.rotate_right_90()
    bossTaVindo.left_pid(8000)
    bossTaVindo.learning_colors()

    print(bossTaVindo.learning_dictionary)


except KeyboardInterrupt:
    bossTaVindo.stop_wheel()

except:
    bossTaVindo.stop_wheel()