#!/usr/bin/env python3

import paho.mqtt.client as mqtt
from ev3dev.ev3 import *
from time import sleep
from simple_pid import *

from robot import Robot

bossTaVindo = Robot()


# bossTaVindo.claw_grab()
# bossTaVindo.claw_delivery()
#bossTaVindo.claw_init()

try:
    bossTaVindo.change_color_mode("COL-COLOR")
    # while 1:
    #     # print("SECONDARY")
    #     # print(bossTaVindo.secondary_brick_values())
    #     #
    #     # print("\nTERTIARY")
    #     # print(bossTaVindo.tertiary_brick_values())
    #     print(bossTaVindo.gyro.value())
    # ini = -3
    # while not (bossTaVindo.search_border()):
    #
    #     if(bossTaVindo.upper_front_ultrassonic.value() / 10) > 35:
    #         print("dist", bossTaVindo.upper_front_ultrassonic.value() / 10)
    #         print()
    #
    #         bossTaVindo.move_motors(200, 200)
    #         ini = time.time()
    #
    #     elif time.time() - ini >= 3:
    #         bossTaVindo.move_motors(300,300)
    #
    # bossTaVindo.change_color_mode("COL-COLOR")

    # print("sai do primeiro whilte")
    ini = -3
    bossTaVindo.claw_init()
    time_init = time.time()

    while not (bossTaVindo.search_border(False)):

        if time.time() - time_init < 5:
            bossTaVindo.move_motors(100,100)

        if (bossTaVindo.upper_front_ultrassonic.value() / 10) > 35 and time.time() - time_init > 5:
            print("dist", bossTaVindo.upper_front_ultrassonic.value() / 10)
            print()

            bossTaVindo.move_motors(200, 200)
            ini = time.time()

        elif time.time() - ini >= 3 and time.time() - time_init > 5:
            bossTaVindo.move_motors(300, 300)

    bossTaVindo.learning_colors()
    print(bossTaVindo.learning_dictionary)


except KeyboardInterrupt:
    bossTaVindo.stop_wheel()

except:
    bossTaVindo.stop_wheel()