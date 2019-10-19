import paho.mqtt.client as mqtt
from time import sleep
from ev3dev.ev3 import *
from datetime import datetime, timedelta

def move_handler(how_long=None, direction="down", speed=50):
    print("move handler")
    global last_direction
    last_direction = direction
    if direction != "down":
        vel = -speed
    else:
        vel = speed

    if how_long is None:
        claw_motor.reset()
        begin = claw_motor.position
        claw_motor.stop_action = 'brake'
        if direction != "down":
            if last_direction != "down":
                counter = 0
                while abs(abs(claw_motor.position) - abs(begin)) < 60:
                    claw_motor.run_forever(speed_sp=vel)
                    if counter > 0:
                        print("tried to rise up grab but was not able")
                    counter += 1
        else:

            claw_motor.run_forever(speed_sp=vel)

        return

    else:
        claw_motor.reset()
        claw_motor.run_forever(speed_sp = -300)
        return


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
    claw_motor.stop_action = 'brake'
    claw_motor.run_forever(speed_sp=-1000)
    sleep(2)
    claw_motor.stop_action = 'hold'
    claw_motor.stop()

def claw_grab():
    claw_motor.stop_action = 'brake'
    claw_motor.run_forever(speed_sp=1000)
    sleep(0.5)
    claw_motor.stop()

def claw_delivery():
    claw_motor.stop_action = 'brake'
    claw_motor.run_forever(speed_sp=1000)
    sleep(1)
    claw_motor.stop_action = 'hold'
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
left_upper_ultrassonic = UltrasonicSensor("in1")

left_lower_ultrassonic.mode = ('US-DIST-CM')
left_upper_ultrassonic.mode = ('US-DIST-CM')

claw_motor = LargeMotor('outB')
claw_motor.stop_action = 'hold'

boolean_claw_init = False
boolean_claw_grab = False
boolean_claw_delivery = False

# print('INIT SECONDARY')
# mB = LargeMotor('outD')
#
# mB.run_forever(speed_sp=-1000)
# mB.wait_while('running')
#
#
# print("OPAAA")
# # while 1:
# #     move_handler(how_long=1,speed=300,direction='up')
# exit(0)
while True:
    if action == 'COL-REFLECT':
        l,r = color_sensor_read('COL-REFLECT', left_sensor,right_sensor)
        print(str(l) + " " + str(r))
        client.publish("robot/secTomain",str(l)+" "+str(r)+" " + str(left_lower_ultrassonic.value() / 10) + " " + str(left_upper_ultrassonic.value() / 10))
        sleep(0.05)
    elif action == 'COL-COLOR':
        l,r = color_sensor_read('COL-COLOR', left_sensor,right_sensor)
        print(l + " " + r)
        client.publish("robot/secTomain",str(l)+" "+str(r)+" " + str(left_lower_ultrassonic.value() / 10) + " " + str(left_upper_ultrassonic.value() / 10))
        sleep(0.05)

    if(boolean_claw_init):
        claw_init()
        boolean_claw_init = False
        Sound.beep()

    elif(boolean_claw_grab):
        claw_grab()
        boolean_claw_grab = False
        Sound.beep()

    elif(boolean_claw_delivery):
        claw_delivery()
        boolean_claw_delivery = False
        Sound.beep()