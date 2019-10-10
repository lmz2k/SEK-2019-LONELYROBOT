import paho.mqtt.client as mqtt
from time import sleep
from ev3dev.ev3 import *


def on_connect(client, userdata, flags, rc):
    client.subscribe("robot/mainTotert")


ip_servidor = "localhost"
client = mqtt.Client()
client.connect(ip_servidor, 1883, 60)
client.on_connect = on_connect
client.loop_start()

left_infrared = InfraredSensor("in1")
right_infrared = InfraredSensor("in2")
left_upper_ultrassonic = UltrasonicSensor("in3")

left_infrared.mode = 'IR-PROX'
right_infrared.mode = 'IR-PROX'
left_upper_ultrassonic.mode = 'US-DIST-CM'

print("SUCESS INIT")

while True:
    client.publish("robot/tertyTomain", str(left_infrared.value()) + " " + str(right_infrared.value()) + " " + str(left_upper_ultrassonic.value() / 10))
    sleep(0.05)
