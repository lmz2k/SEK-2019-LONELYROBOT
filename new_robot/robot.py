#!/usr/bin/env python3

import paho.mqtt.client as mqtt
from ev3dev.ev3 import *
from time import sleep
from simple_pid import *

class Robot():

    def __init__(self):

        self.DESTINY_TO_MAIN = "robot/secTomain"
        self.DESTINY_TO_SEC = "robot/mainTosec"
        self.DESTINY_FROM_TERTIATY = "robot/tertyTomain"

        self.left_wheel = LargeMotor('outA')
        self.right_wheel = LargeMotor('outD')
        self.left_claw = LargeMotor('outC')
        self.right_claw = LargeMotor('outB')

        self.left_ultrassonic = UltrasonicSensor('in4')
        self.right_ultrassonic = UltrasonicSensor('in3')
        self.upper_front_ultrassonic = UltrasonicSensor('in2')
        self.gyro = GyroSensor('in1')


        self.upper_front_ultrassonic.mode = 'US-DIST-CM'
        self.left_ultrassonic.mode = 'US-DIST-CM'
        self.right_ultrassonic.mode = 'US-DIST-CM'
        self.gyro.mode = 'GYRO-ANG'

        ##Secondary Brick

        self.left_color_sensor = None
        self.right_color_sensor = None

        self.left_lower_ultrassonic = None

        self.secondary_brick_ip = "10.42.0.3"
        self.secondary_connection = mqtt.Client()
        self.secondary_connection.connect(self.secondary_brick_ip, 1883, 60)
        self.secondary_connection.on_connect = self.on_connect_secondary
        self.secondary_connection.on_message = self.on_message_secondary
        self.secondary_connection.loop_start()

        ##Tertiary Brick

        self.left_infrared = None
        self.right_infrared = None

        self.left_upper_ultrassonic = None

        self.tertiary_brick_ip = "192.168.2.39"
        self.tertiary_connection = mqtt.Client()
        self.tertiary_connection.connect(self.tertiary_brick_ip, 1883, 60)
        self.tertiary_connection.on_connect = self.on_connect_tertiary
        self.tertiary_connection.on_message = self.on_message_tertiary
        self.tertiary_connection.loop_start()

    def on_connect_secondary(self, client, userdata, flags, rc):
        print("SECONDARY BRICK CONNECTION SUCESS!!!!")
        client.subscribe(self.DESTINY_TO_MAIN)

    def on_message_secondary(self, client, userdata, msg):
        mensagem = msg.payload.decode().split()
        self.left_color_sensor = mensagem[0]
        self.right_color_sensor = mensagem[1]
        self.left_lower_ultrassonic = mensagem[2]

    def on_connect_tertiary(self, client, userdata, flags, rc):
        print("TERTIARY BRICK CONNECTION SUCESS!!!!")
        client.subscribe(self.DESTINY_FROM_TERTIATY)

    def on_message_tertiary(self, client, userdata, msg):
        mensagem = msg.payload.decode().split()
        self.left_infrared = int(mensagem[0])
        self.right_infrared = int(mensagem[1])
        self.left_upper_ultrassonic = float(mensagem[2])

    def gyro_reset(self):
        self.gyro.mode = 'GYRO-RATE'
        self.gyro.mode = 'GYRO-ANG'

    def motors_position_reset(self):
        self.left_wheel.position = 0
        self.right_wheel.position = 0

    def claw_position_reset(self):
        self.left_claw.position = 0
        self.right_claw.position = 0

    def change_color_mode(self, color_mode):

        if color_mode == 'COL-REFLECT':
            self.secondary_connection.publish(self.DESTINY_TO_SEC, 'COL-REFLECT'+' '+'None')

            while not self.left_color_sensor.isdigit() or not self.right_color_sensor.isdigit():
                pass

        else:
            self.secondary_connection.publish(self.DESTINY_TO_SEC, 'COL-COLOR'+' '+'None')
            while self.left_color_sensor.isdigit() and self.right_color_sensor.isdigit():
                pass

    def secondary_brick_values(self):
        return self.left_color_sensor,self.right_color_sensor,self.left_lower_ultrassonic

    def tertiary_brick_values(self):
        return self.left_infrared,self.right_infrared,self.left_upper_ultrassonic

    def claw_init(self):
        self.secondary_connection.publish(self.DESTINY_TO_SEC,'COL-COLOR'+" "+"INIT")

    def claw_grab(self):
        self.secondary_connection.publish(self.DESTINY_TO_SEC, 'COL-REFLECT' + " " + "GRAB")

    def claw_delivery(self):
        self.secondary_connection.publish(self.DESTINY_TO_SEC, 'COL-REFLECT' + " " + "DELIVERY")

    def init_robot(self):
        self.change_color_mode('COL-COLOR')
        self.claw_init()
