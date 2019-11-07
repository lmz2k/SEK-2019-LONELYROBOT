#!/usr/bin/env python3

import paho.mqtt.client as mqtt
from ev3dev.ev3 import *
from time import sleep
from simple_pid import *

from robot import Robot

bossTaVindo = Robot()
pipe_size = 10
start_of_round = False



while not bossTaVindo.initial_posotion_start:
    bossTaVindo.btn.process()
    print('PRESS ME')

try:
    ########## Início ###########################
    while True:
        bossTaVindo.open_claws()
        bossTaVindo.claw_init()
        bossTaVindo.change_color_mode('COL-COLOR')
        sleep(2)

        while not (bossTaVindo.search_border(start_of_round)):
            bossTaVindo.move_motors_run_forever(300, 300)

        if not (start_of_round):
            bossTaVindo.learning_colors()
            print(bossTaVindo.learning_dictionary)
            start_of_round = True

        else:
            bossTaVindo.rotate_right_90()
            bossTaVindo.move_motors_run_forever(200, 200)
            while bossTaVindo.left_color_sensor == 'white' and bossTaVindo.right_color_sensor == 'white': pass
            bossTaVindo.stop_wheel()
            bossTaVindo.color_alignment(['black'], bossTaVindo.PIPE_AREA, ['white'])
            bossTaVindo.move_motors_run_forever(-100, -100)
            sleep(0.5)
            bossTaVindo.stop_wheel()
            bossTaVindo.rotate_right_90()

        condition = bossTaVindo.LOST_PIPE
        while condition == bossTaVindo.LOST_PIPE:
            while not (bossTaVindo.searching_closer_pipe()) : pass
            bossTaVindo.move_motors_run_forever(200, 200)
            sleep(1.5)
            bossTaVindo.stop_wheel()
            if not (bossTaVindo.toward_the_pipe()):
                bossTaVindo.stop_wheel()
                continue
            condition = bossTaVindo.grab_the_pipe()
        while not (bossTaVindo.search_border(False)):
            bossTaVindo.move_motors_run_forever(300, 300)
        bossTaVindo.prepare_to_dive()
        bossTaVindo.go_down_to_pipeline()
        bossTaVindo.deep_area_pipe_following()
        bossTaVindo.go_up_to_meeting_area()
        bossTaVindo.DEFAULT_PIPE = 10

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