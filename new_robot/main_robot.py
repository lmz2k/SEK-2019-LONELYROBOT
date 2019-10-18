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
bossTaVindo.change_color_mode('COL-COLOR')
pipe_size = 10
sleep(1)

try:

    ########## Início
    ini = -3
    bossTaVindo.claw_init()
    sleep(1)
    time_init = time.time()

    while not (bossTaVindo.search_border(False)):

        if time.time() - time_init < 5:
            bossTaVindo.move_motors(100,100)

        else:
            bossTaVindo.move_motors(300, 300)

    bossTaVindo.learning_colors()
    print(bossTaVindo.learning_dictionary)

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
    bossTaVindo.go_down_to_pipeline()
    bossTaVindo.pipeline_support_following()

    while 1:
        print(bossTaVindo.middle_ultrasonic_sensors())
except KeyboardInterrupt:
    bossTaVindo.stop_wheel()
    bossTaVindo.left_claw.stop_action = 'brake'
    bossTaVindo.right_claw.stop_action = 'brake'
    bossTaVindo.right_claw.stop()
    bossTaVindo.left_claw.stop()

except:
    bossTaVindo.stop_wheel()
    bossTaVindo.left_claw.stop_action = 'brake'
    bossTaVindo.right_claw.stop_action = 'brake'
    bossTaVindo.right_claw.stop()
    bossTaVindo.left_claw.stop()
    raise