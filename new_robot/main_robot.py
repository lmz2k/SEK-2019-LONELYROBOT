#!/usr/bin/env python3

import paho.mqtt.client as mqtt
from ev3dev.ev3 import *
from time import sleep
from simple_pid import *

from robot import Robot

bossTaVindo = Robot()

#
# while 1:
#     bossTaVindo.open_claws()

# bossTaVindo.claw_grab()
# bossTaVindo.claw_delivery()

bossTaVindo.open_claws()
bossTaVindo.claw_init()
pipe_size = 10


# while 1:
#     print("levantando")
#     bossTaVindo.claw_init()
#     sleep(5)
#     print("grab")
#     bossTaVindo.claw_grab()
#     sleep(5)
#     print("delivery")
#     bossTaVindo.claw_delivery()
#     sleep(5)

try:
    while 1:
        bossTaVindo.left_pid(bossTaVindo.INFINITY)

    while 1:
        bossTaVindo.move_motors(1000,1000)

    while 1:
        bossTaVindo.pipeline_support_following()
    bossTaVindo.stop_wheel()
    # ini = -3
    # bossTaVindo.claw_init()
    # sleep(1)
    # time_init = time.time()
    #
    # while not (bossTaVindo.search_border(False)):
    #
    #     if time.time() - time_init < 5:
    #         bossTaVindo.move_motors(100,100)
    #
    #     else:
    #         bossTaVindo.move_motors(300, 300)
    #
    # bossTaVindo.learning_colors()
    # print(bossTaVindo.learning_dictionary)

    boole = False
    while not boole:
        while not (bossTaVindo.searching_closer_pipe()) : pass
        bossTaVindo.move_motors(200,200)
        sleep(1.5)
        bossTaVindo.stop_wheel()
        boole = bossTaVindo.toward_the_pipe()
    bossTaVindo.stop_wheel()
    bossTaVindo.grab_the_pipe()
    bossTaVindo.prepare_to_dive()
    # #
    # bossTaVindo.stop_wheel()
    # bossTaVindo.get_closer_with_the_pipe()
    # print(bossTaVindo.getting_the_pipe())

    # bossTaVindo.open_claws()
    #
    # sleep(10)
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