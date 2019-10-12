#!/usr/bin/env python3

import paho.mqtt.client as mqtt
from ev3dev.ev3 import *
from time import sleep
from simple_pid import *

from robot import Robot

bossTaVindo = Robot()


# bossTaVindo.claw_grab()
# bossTaVindo.claw_delivery()

# bossTaVindo.claw_init()
# bossTaVindo.open_claws()
# pipe_size = 15

# bossTaVindo.rotate_left_90()
# while 1: pass

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
    sleep(1)
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

    while not (bossTaVindo.searching_closer_pipe()) : pass

    bossTaVindo.move_motors(200,200)
    sleep(1.5)
    bossTaVindo.stop_wheel()
    bossTaVindo.toward_the()
    # pipe_alignment = bossTaVindo.getting_the_pipe()
    #
    # if(pipe_alignment == "lost"):
    #     print(bossTaVindo.middle_ultrasonic_sensors())
    #     sleep(5)
    #     pipe_alignment = bossTaVindo.verify_the_pipe_is()
    #
    # print(pipe_alignment)
    #
    # if(pipe_alignment == 'parallel'):
    #     bossTaVindo.open_claws()
    #     bossTaVindo.move_motors(-200,-200)
    #     sleep(0.75)
    #     bossTaVindo.stop_wheel()
    #     bossTaVindo.claw_grab()
    #     sleep(2)
    #     bossTaVindo.move_motors(200,200)
    #     # left,right = bossTaVindo.middle_ultrasonic_sensors()
    #     # while left > 3 and right > 3: pass
    #     init = time.time()
    #     while time.time() - init < 2: pass
    #     bossTaVindo.claw_init()
    #     sleep(0.25)
    #     bossTaVindo.stop_wheel()
    #
    # elif(pipe_alignment == "perpendicular"):
    #     bossTaVindo.angle_reset()
    #     Sound.beep()
    #     bossTaVindo.change_color_mode('COL-COLOR')
    #     bossTaVindo.move_motors(-100,-100)
    #     while bossTaVindo.left_color_sensor in bossTaVindo.PIPE_AREA and  bossTaVindo.right_color_sensor in bossTaVindo.PIPE_AREA:pass
    #     bossTaVindo.stop_wheel()
    #
    #     bossTaVindo.color_alignment(["black"], bossTaVindo.PIPE_AREA, ["white"])
    #
    #     if(pipe_size == 15):
    #         bossTaVindo.re_pipe(pipe_size)
    #
    # bossTaVindo.left_claw.stop_action = "brake"
    # bossTaVindo.right_claw.stop_action = "brake"
    # bossTaVindo.right_claw.stop()
    # bossTaVindo.left_claw.stop()

    while 1:
        print(bossTaVindo.middle_ultrasonic_sensors())
except KeyboardInterrupt:
    bossTaVindo.stop_wheel()

except:
    bossTaVindo.stop_wheel()
    raise