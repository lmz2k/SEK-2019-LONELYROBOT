#!/usr/bin/env python3

import paho.mqtt.client as mqtt
from time import sleep
from ev3dev.ev3 import *
from datetime import datetime, timedelta

def color_sensor_read(mode,left_sensor,right_sensor):
    colors = ('unknown', 'black', 'blue', 'green', 'yellow', 'red', 'white', 'brown')

    left_sensor.mode = mode
    right_sensor.mode = mode

    if mode == 'COL-COLOR':

        right = colors[right_sensor.value()]
        left = colors[left_sensor.value()]

        if right == 'brown':
            right = 'black'
        if left == 'brown':
            left = 'black'

        return left, right

    return left_sensor.value(),right_sensor.value()

def claw_init():
    print("SUBIDA")
    claw_motor.stop_action = 'brake'
    claw_motor.run_forever(speed_sp=-1000)
    sleep(2)
    claw_motor.stop_action = 'hold'
    claw_motor.stop()

def claw_grab():
    print("DESCIDA")
    claw_motor.stop_action = 'brake'
    claw_motor.run_forever(speed_sp=1000)
    sleep(2)
    claw_motor.stop()

def claw_delivery():
    claw_motor.stop_action = 'brake'
    # claw_motor.run_forever(speed_sp=1000)
    # sleep(1)
    # claw_motor.stop_action = 'hold'
    # claw_motor.stop()
    init = time.time()
    while time.time() - init < 8:
        claw_motor.run_forever(speed_sp = 50)
        sleep(0.25)
        claw_motor.run_forever(speed_sp = -25)
        sleep(0.25)
    claw_motor.stop()

def on_connect(client, userdata, flags, rc):
    client.subscribe("robot/mainTosec")


def on_message( client, userdata, msg):
        global action
        global boolean_claw_init
        global boolean_claw_grab
        global boolean_claw_delivery

        mensagem = msg.payload.decode().split()
        action = mensagem[0]
        motor_action = mensagem[1]

        if motor_action == 'INIT':
            boolean_claw_init = True

        elif motor_action == 'GRAB':
            boolean_claw_grab = True

        elif motor_action == 'DELIVERY':
            boolean_claw_delivery = True

action = 'COL-COLOR'
last_direction = None

ip_servidor = "localhost"
client = mqtt.Client()
client.connect(ip_servidor, 1883, 60)
client.on_connect = on_connect
client.on_message = on_message
client.loop_start()

left_sensor = ColorSensor('in4')
right_sensor = ColorSensor('in3')

left_lower_ultrassonic = UltrasonicSensor('in2')
left_upper_infrared = UltrasonicSensor("in1")

left_lower_ultrassonic.mode = 'US-DIST-CM'
left_upper_infrared.mode = 'US-DIST-CM'

claw_motor = LargeMotor('outB')
claw_motor.stop_action = 'hold'

boolean_claw_init = False
boolean_claw_grab = False
boolean_claw_delivery = False
print("SERVIDOR INICIADO COM SUCESSO!")

try:
    while True:
        if action == 'COL-REFLECT':
            l,r = color_sensor_read('COL-REFLECT', left_sensor,right_sensor)
            # print(str(l) + " " + str(r))
            client.publish("robot/secTomain", str(l) +" " + str(r) +" " + str(left_lower_ultrassonic.value() / 10) + " " + str(left_upper_infrared.value()/10))
            sleep(0.05)
        elif action == 'COL-COLOR':
            l,r = color_sensor_read('COL-COLOR', left_sensor,right_sensor)
            # print(l + " " + r)
            client.publish("robot/secTomain", str(l) +" " + str(r) +" " + str(left_lower_ultrassonic.value() / 10) + " " + str(left_upper_infrared.value()/10))
            sleep(0.05)

        if(boolean_claw_init):
            claw_init()
            boolean_claw_init = False

        elif(boolean_claw_grab):
            claw_grab()
            boolean_claw_grab = False

        elif(boolean_claw_delivery):
            claw_delivery()
            boolean_claw_delivery = False

except KeyboardInterrupt:
    claw_motor.stop_action = 'brake'
    claw_motor.stop()




