import paho.mqtt.client as mqtt
from ev3dev.ev3 import *
from time import sleep
from simple_pid import *
import math
from datetime import datetime, timedelta

DEFAULT_SPEED = 500

class Robot():

    def __init__(self):

        self.PIPE_FROM_THE_HOLE = 'PIPE_FROM_THE_HOLE'
        self.PIPE_FROM_THE_BORDER = 'PIPE_FROM_THE_BORDER'
        self.WALL_DISTANCE = 5
        self.INFINITY = 999999
        self.DEFAULT_PASSES = 1600
        self.DEFAULT_SPEED = 500
        self.DEFAULT_PIPE = 10
        self.PIPE_AREA = ['blue', 'red', 'yellow']
        self.PIPE_AREA_DICTIONARY = {'yellow': 10, 'red' : 15, 'blue' : 20}
        self.DESTINY_TO_MAIN = "robot/secTomain"
        self.DESTINY_TO_SEC = "robot/mainTosec"
        self.DESTINY_FROM_TERTIATY = "robot/tertyTomain"

        self.left_wheel = LargeMotor('outA')
        self.right_wheel = LargeMotor('outD')
        self.left_claw = MediumMotor('outC')
        self.right_claw = MediumMotor('outB')

        self.right_claw.polarity = "inversed"

        # self.left_claw.stop_action = "hold"
        # self.right_claw.stop_action = "hold"

        self.left_ultrassonic = UltrasonicSensor('in4')
        self.right_ultrassonic = UltrasonicSensor('in3')
        self.infrared = InfraredSensor('in2')
        self.gyro = GyroSensor('in1')

        self.infrared.mode = 'IR-PROX'
        self.left_ultrassonic.mode = 'US-DIST-CM'
        self.right_ultrassonic.mode = 'US-DIST-CM'
        self.gyro.mode = 'GYRO-ANG'

        ##Secondary Brick

        self.left_color_sensor = "None"
        self.right_color_sensor = "None"

        self.left_lower_ultrassonic = None
        self.left_upper_ultrassonic = None

        self.secondary_brick_ip = "10.42.0.3"
        self.secondary_connection = mqtt.Client()
        self.secondary_connection.connect(self.secondary_brick_ip, 1883, 60)
        self.secondary_connection.on_connect = self.on_connect_secondary
        self.secondary_connection.on_message = self.on_message_secondary
        self.secondary_connection.loop_start()

        ##Tertiary Brick

        # self.left_infrared = None
        # self.right_infrared = None
        #
        # self.left_upper_ultrassonic = None
        #
        # self.tertiary_brick_ip = "192.168.2.39"
        # self.tertiary_connection = mqtt.Client()
        # self.tertiary_connection.connect(self.tertiary_brick_ip, 1883, 60)
        # self.tertiary_connection.on_connect = self.on_connect_tertiary
        # self.tertiary_connection.on_message = self.on_message_tertiary
        # self.tertiary_connection.loop_start()

        ##OTHERS
        self.pipe_dimesion = self.DEFAULT_PIPE
        # self.learning_dictionary = {}
        self.learning_dictionary = {15: 1600 * 2.2, 10: 1600, 20: 1600 * 3.34}
        self.init_wheel_position = 0

    def on_connect_secondary(self, client, userdata, flags, rc):
        print("SECONDARY BRICK CONNECTION SUCESS!!!!")
        client.subscribe(self.DESTINY_TO_MAIN)

    def on_message_secondary(self, client, userdata, msg):
        mensagem = msg.payload.decode().split()
        self.left_color_sensor = mensagem[0]
        self.right_color_sensor = mensagem[1]
        self.left_lower_ultrassonic = float(mensagem[2])
        self.left_upper_ultrassonic = float(mensagem[3])

    # def on_connect_tertiary(self, client, userdata, flags, rc):
    #     print("TERTIARY BRICK CONNECTION SUCESS!!!!")
    #     client.subscribe(self.DESTINY_FROM_TERTIATY)
    #
    # def on_message_tertiary(self, client, userdata, msg):
    #     mensagem = msg.payload.decode().split()
    #     self.left_infrared = int(mensagem[0])
    #     self.right_infrared = int(mensagem[1])
    #     self.left_upper_ultrassonic = float(mensagem[2])

    def gyro_reset(self):
        self.gyro.mode = 'GYRO-RATE'
        self.gyro.mode = 'GYRO-ANG'

    def motors_position_reset(self, passes = 0):
        self.left_wheel.position = passes
        self.right_wheel.position = passes

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
            while self.left_color_sensor.isdigit() or self.right_color_sensor.isdigit():
                pass

    def secondary_brick_values(self):
        return self.left_color_sensor,self.right_color_sensor,self.left_lower_ultrassonic,self.left_upper_ultrassonic

    # def tertiary_brick_values(self):
    #     return self.left_infrared,self.right_infrared,self.left_upper_ultrassonic

    def angle_reset(self):

        angle = self.gyro.value()
        print(angle)

        if (angle > 0):
            self.left_wheel.run_forever(speed_sp=-200)
            self.right_wheel.run_forever(speed_sp=200)
            while (self.gyro.value() > 0):
                print("ajustando para a esquerda= " + str(self.gyro.value()))


        elif (angle < 0):
            self.left_wheel.run_forever(speed_sp=200)
            self.right_wheel.run_forever(speed_sp=-200)
            while (self.gyro.value() < 0):
                print("ajustando para a direita= " + str(self.gyro.value()))

        self.stop_wheel()

    def claw_init(self):
        self.secondary_connection.publish(self.DESTINY_TO_SEC,'COL-COLOR'+" "+"INIT")

    def claw_grab(self):
        self.secondary_connection.publish(self.DESTINY_TO_SEC, 'COL-REFLECT' + " " + "GRAB")

    def claw_delivery(self):
        self.secondary_connection.publish(self.DESTINY_TO_SEC, 'COL-REFLECT' + " " + "DELIVERY")

    def init_robot(self):
        self.change_color_mode('COL-COLOR')
        self.claw_init()

    def stop_wheel(self):
        self.left_wheel.stop()
        self.right_wheel.stop()

    def color_alignment(self, expected_color, front, back):

        self.change_color_mode('COL-COLOR')
        cont = 0

        while self.left_color_sensor not in expected_color or self.right_color_sensor not in expected_color:

            if(cont == 5):
                print("conte 5??")
                return False

            for cont in range(6):

                while self.left_color_sensor in front:
                    self.left_wheel.run_forever(speed_sp=-100)
                self.stop_wheel()

                while self.left_color_sensor in back:
                    self.left_wheel.run_forever(speed_sp=100)
                self.stop_wheel()

                while self.right_color_sensor in front:
                    self.right_wheel.run_forever(speed_sp=-100)
                self.stop_wheel()

                while self.right_color_sensor in back:
                    self.right_wheel.run_forever(speed_sp=100)
                self.stop_wheel()

        return True

    def color_black_verify(self,border):

        self.change_color_mode('COL-REFLECT')

        print("valores: ",self.right_color_sensor, self.left_color_sensor)

        if(int(self.right_color_sensor) == 0 or int(self.left_color_sensor) == 0):
            print("entrei no 0")
            self.change_color_mode('COL-COLOR')
            self.move_motors(-200,-200)
            while(self.right_color_sensor != "white" or self.left_color_sensor != "white"):print("to aqui")
            self.stop_wheel()

            print("antes")
            self.color_alignment(["white"], ["black","unknown"], [])
            print("depois")

            self.move_motors(-200,-200)
            sleep(1.5)
            self.stop_wheel()

            if(border):
                self.rotate_right_90()
            else:
                self.rotate_left_90()
            return True

        elif(int(self.right_color_sensor) == 6 or int(self.left_color_sensor) == 6):
            print("entrei no 6")
            self.change_color_mode('COL-COLOR')
            self.move_motors(-200, -200)
            while (self.right_color_sensor != "white" and self.left_color_sensor != "white"): pass
            self.stop_wheel()
            self.color_alignment(["white"], ["black", "green","unknown"], [])

            self.move_motors(-200, -200)
            sleep(1.5)
            self.stop_wheel()
            self.rotate_right_90()
            self.rotate_right_90()
            return True
        self.change_color_mode('COL-COLOR')
        return False

    def search_border(self, border = True): ##se border == True ele vai ir para o borda esquerda, caso não, borda direita

        self.change_color_mode('COL-COLOR')

        if(self.left_color_sensor == "green" or self.right_color_sensor == "green"):
            print("Green case")
            self.color_alignment(["green"], [], ["white"])
            self.move_motors(-200,-200)
            sleep(1.5)

            self.rotate_right_90()
            self.rotate_right_90()
            return False

        elif(self.left_color_sensor == "black" or self.right_color_sensor == "black"):
            print("Black case")
            self.stop_wheel()
            if(self.color_black_verify(border)):
                return False

            if(self.color_alignment(["black"], self.PIPE_AREA, ["white"])):
                self.stop_wheel()
                self.move_motors(-100, -100)
                sleep(0.5)
                self.stop_wheel()
                if(border):
                    self.rotate_left_90()
                    self.right_pid(self.INFINITY)
                    self.change_color_mode('COL-COLOR')
                    self.move_motors(-100, -100)
                    while self.left_color_sensor != 'white' and self.right_color_sensor != 'white': pass
                    self.stop_wheel()

                else:
                    self.rotate_right_90()
                    self.left_pid(self.INFINITY)
                    self.change_color_mode('COL-COLOR')
                    self.move_motors(-100, -100)
                    while self.left_color_sensor != 'white' and self.right_color_sensor != 'white': pass
                    self.stop_wheel()

                self.move_motors(-200, -200)
                sleep(2)
                self.stop_wheel()
                return True

            else:
                self.move_motors(-100,-100)
                sleep(1)
                self.stop_wheel()

            # else:
            #
            #     self.move_motors(-100, -100)
            #     while self.left_color_sensor == 'white' or self.right_color_sensor == 'white': pass
            #     self.stop_wheel()

        elif(self.left_color_sensor == "unknown" or self.right_color_sensor == "unknown"):
            print("Unknown case")

            if(self.left_color_sensor == "unknown"):
                while(self.left_color_sensor != self.right_color_sensor):
                    self.move_motors(-200,200)
                self.stop_wheel()

            elif (self.right_color_sensor == "unknown"):
                while (self.left_color_sensor != self.right_color_sensor):
                    self.move_motors(200, -200)
                self.stop_wheel()

            self.move_motors(-200,-200)
            sleep(1.5)
            self.stop_wheel()
            if (border):
                self.rotate_right_90()

            else:
                self.rotate_left_90()

            return False
        print("Falso")
        return False

    def move_motors(self, left_speed = DEFAULT_SPEED, right_speed = DEFAULT_SPEED):

        self.left_wheel.run_forever(speed_sp = left_speed)
        self.right_wheel.run_forever(speed_sp = right_speed)

    def rotate_left_90(self):
        self.gyro_reset()
        self.move_motors(-150,150)
        while (self.gyro.value() > -88) : pass
        self.stop_wheel()
        self.gyro_reset()
        self.gyro_reset()

    def rotate_right_90(self):
        self.gyro_reset()
        self.move_motors(300,-300)
        while (self.gyro.value() < 88) : pass
        self.stop_wheel()
        self.gyro_reset()
        self.gyro_reset()

    def right_pid_to_grab(self):
        self.gyro_reset()
        self.change_color_mode('COL-REFLECT')
        self.right_wheel.position = 0
        default = 200
        pid = PID(1.025, 0, 0.9, setpoint=39)

        max_speed_bound = 500
        max_control = max_speed_bound - default
        min_control = -max_speed_bound + default
        entrar = True
        while (int(self.left_color_sensor) != 0 and int(self.right_color_sensor) != 0):

            control = pid(int(self.right_color_sensor))

            if self.right_wheel.position > 100:
                self.claw_init()

            if (self.gyro.value() > 25):
                self.stop_wheel()
                self.change_color_mode("COL-COLOR")

                while self.right_color_sensor in self.PIPE_AREA:
                    self.move_motors(-200, -200)
                self.stop_wheel()

                while self.right_color_sensor in self.PIPE_AREA or self.right_color_sensor == 'black':
                    self.right_wheel.run_forever(speed_sp=200)

                self.stop_wheel()
                self.change_color_mode("COL-REFLECT")
                self.gyro_reset()

            if control > max_control:
                control = max_speed_bound - default
            elif control < min_control:
                control = -max_speed_bound + default

            self.right_wheel.run_forever(speed_sp=default + control)
            self.left_wheel.run_forever(speed_sp=default - control)

        self.stop_wheel()

    def right_pid(self,distance, claw_grab = False):
        self.gyro_reset()
        self.change_color_mode('COL-REFLECT')
        self.right_wheel.position = 0
        default = 200
        pid = PID(1.025, 0, 0.9, setpoint=39)

        max_speed_bound = 500
        max_control = max_speed_bound - default
        min_control = -max_speed_bound + default
        entrar = True
        while self.right_wheel.position < distance and (int(self.left_color_sensor) != 0 and int(self.right_color_sensor) != 0):

            control = pid(int(self.right_color_sensor))

            if (claw_grab and (max(self.middle_ultrasonic_sensors())) < 5):
                self.stop_wheel()
                self.right_pid_to_grab()
                break

            if self.right_wheel.position > 200 and entrar:
                entrar = False
                self.gyro_reset()
                default = 300
                pid.tunings = (1.025, 0, 0.9)

            if (self.gyro.value() > 25):
                self.stop_wheel()
                self.change_color_mode("COL-COLOR")

                while self.right_color_sensor in self.PIPE_AREA:
                    self.move_motors(-200, -200)
                self.stop_wheel()

                while self.right_color_sensor in self.PIPE_AREA or self.right_color_sensor == 'black':
                    self.right_wheel.run_forever(speed_sp=200)

                self.stop_wheel()
                self.change_color_mode("COL-REFLECT")
                self.gyro_reset()

            if control > max_control:
                control = max_speed_bound - default
            elif control < min_control:
                control = -max_speed_bound + default

            self.right_wheel.run_forever(speed_sp=default + control)
            self.left_wheel.run_forever(speed_sp=default - control)

        self.stop_wheel()

    def left_pid_to_grab(self):
        self.move_motors(-200,-200)
        sleep(1)
        self.stop_wheel()
        self.claw_grab()

        self.gyro_reset()
        self.change_color_mode('COL-REFLECT')
        self.left_wheel.position = 0

        default = 200
        pid = PID(1.025, 0, 0.13, setpoint=39)

        max_speed_bound = 500
        max_control = max_speed_bound - default
        min_control = -max_speed_bound + default

        while (int(self.left_color_sensor) != 0 and int(self.right_color_sensor) != 0):
            print("gyro Left   " + str(self.gyro.value()))

            control = pid(int(self.left_color_sensor))

            if (self.left_wheel.position > 500):
                self.claw_init()
                break

            if (self.gyro.value() < -25):

                self.stop_wheel()
                self.change_color_mode("COL-COLOR")

                while self.left_color_sensor in self.PIPE_AREA:
                    self.move_motors(-200, -200)
                self.stop_wheel()

                while self.left_color_sensor == "white":
                    self.move_motors(200, 200)
                sleep(0.5)
                self.stop_wheel()

                while self.left_color_sensor in self.PIPE_AREA or self.left_color_sensor == 'black':
                    self.left_wheel.run_forever(speed_sp=200)

                self.stop_wheel()
                self.change_color_mode("COL-REFLECT")
                self.gyro_reset()

            if control > max_control:
                control = max_speed_bound - default
            elif control < min_control:
                control = -max_speed_bound + default

            self.right_wheel.run_forever(speed_sp=default - control)
            self.left_wheel.run_forever(speed_sp=default + control)

        self.stop_wheel()

    def left_pid(self, distance, claw_grab = False):

        self.gyro_reset()
        self.change_color_mode('COL-REFLECT')
        self.left_wheel.position = 0

        default = 200
        pid = PID(1.025, 0, 0.13, setpoint=39)

        max_speed_bound = 500
        max_control = max_speed_bound - default
        min_control = -max_speed_bound + default
        entrar = True
        while self.left_wheel.position < distance and (int(self.left_color_sensor) != 0 and int(self.right_color_sensor) != 0):
            print("gyro Left   " + str(self.gyro.value()))

            control = pid(int(self.left_color_sensor))
            if(claw_grab and (max(self.middle_ultrasonic_sensors())) <= 10):
                self.stop_wheel()
                self.left_pid_to_grab()
                break

            if self.left_wheel.position > 200 and entrar:
                entrar = False
                self.gyro_reset()
                default = 300
                pid.tunings = (1.025, 0, 0.13)

            if (self.gyro.value() < -25):

                self.stop_wheel()
                self.change_color_mode("COL-COLOR")

                while self.left_color_sensor in self.PIPE_AREA:
                    self.move_motors(-200,-200)
                self.stop_wheel()

                while self.left_color_sensor == "white":
                    self.move_motors(200,200)
                sleep(0.5)
                self.stop_wheel()

                while self.left_color_sensor in self.PIPE_AREA or self.left_color_sensor == 'black':
                    self.left_wheel.run_forever(speed_sp=200)

                self.stop_wheel()
                self.change_color_mode("COL-REFLECT")
                self.gyro_reset()

            if control > max_control:
                control = max_speed_bound - default
            elif control < min_control:
                control = -max_speed_bound + default

            self.right_wheel.run_forever(speed_sp=default - control)
            self.left_wheel.run_forever(speed_sp=default + control)

        self.stop_wheel()

    def pid_adjustment(self, sensor):

        if(sensor == 'left'):
            self.move_motors(-200,-200)
            while(self.left_color_sensor in self.PIPE_AREA): pass
            self.stop_wheel()

            self.move_motors(200,0)
            while(self.left_color_sensor in self.PIPE_AREA or self.left_color_sensor == 'black'): pass
            self.stop_wheel()

        elif(sensor == "right"):
            self.move_motors(-200, -200)
            while (self.right_color_sensor in self.PIPE_AREA): pass
            self.stop_wheel()

            self.move_motors(0,200)
            while (self.right_color_sensor in self.PIPE_AREA or self.right_color_sensor == 'black'): pass
            self.stop_wheel()

    def learning_colors(self):
        self.rotate_left_90()
        self.color_alignment(["black"], self.PIPE_AREA, ["white"])

        self.move_motors()
        while self.left_color_sensor not in self.PIPE_AREA or self.right_color_sensor not in self.PIPE_AREA: pass
        self.stop_wheel()

        self.learning_dictionary[self.PIPE_AREA_DICTIONARY[self.left_color_sensor]] = self.DEFAULT_PASSES * 3.34

        self.move_motors(-200,-200)
        while self.left_color_sensor in self.PIPE_AREA or self.right_color_sensor in self.PIPE_AREA: pass
        self.stop_wheel()

        self.color_alignment(["black"], self.PIPE_AREA, ["white"])

        self.move_motors(-100,-100)
        sleep(0.5)
        self.stop_wheel()

        self.rotate_left_90()
        self.right_pid(self.DEFAULT_PASSES + 500)

        self.change_color_mode('COL-COLOR')
        self.rotate_right_90()
        self.move_motors()
        while self.left_color_sensor not in self.PIPE_AREA or self.right_color_sensor not in self.PIPE_AREA: pass
        self.stop_wheel()

        self.learning_dictionary[self.PIPE_AREA_DICTIONARY[self.left_color_sensor]] = self.DEFAULT_PASSES*2.2

        for pipe in self.PIPE_AREA_DICTIONARY.values():
            if(pipe not in self.learning_dictionary.keys()):
                self.learning_dictionary[pipe] = self.DEFAULT_PASSES
                break

        self.move_motors(-200, -200)
        while self.left_color_sensor in self.PIPE_AREA or self.right_color_sensor in self.PIPE_AREA: pass
        self.stop_wheel()

        self.color_alignment(["black"], self.PIPE_AREA, ["white"])

        self.move_motors(-100, -100)
        sleep(0.5)
        self.stop_wheel()
        self.rotate_left_90()
        self.right_pid(self.INFINITY)
        self.move_motors(-200, -200)
        sleep(2)
        self.stop_wheel()
        self.rotate_right_90()
        self.move_motors(100, 100)
        while self.left_color_sensor == 'white' and self.right_color_sensor == 'white': pass
        self.stop_wheel()
        self.color_alignment(["black"], self.PIPE_AREA, ["white"])
        self.move_motors(-100, -100)
        sleep(0.5)
        self.stop_wheel()
        self.rotate_right_90()

    def searching_closer_pipe(self):

        self.gyro_reset()
        self.change_color_mode('COL-REFLECT')
        self.left_wheel.position = 0

        default = 200
        pid = PID(1.025, 0, 0.13, setpoint=39)
        closer_pipe_passes = 0

        max_speed_bound = 500
        max_control = max_speed_bound - default
        min_control = -max_speed_bound + default

        passes = self.learning_dictionary[self.DEFAULT_PIPE]
        self.motors_position_reset(self.init_wheel_position)
        small_read = self.INFINITY
        entry = True

        while(self.left_wheel.position < passes and int(self.left_color_sensor) > 0):

            control = pid(int(self.left_color_sensor))
            if self.left_wheel.position > 200 and entry:
                entry = False
                self.gyro_reset()
                default = 300
                pid.tunings = (1.025, 0, 0.13,)

            if (self.gyro.value() < -25):

                self.stop_wheel()
                self.change_color_mode("COL-COLOR")

                while self.left_color_sensor in self.PIPE_AREA:
                    self.move_motors(-200,-200)
                self.stop_wheel()

                while self.left_color_sensor in self.PIPE_AREA or self.left_color_sensor == 'black':
                    self.left_wheel.run_forever(speed_sp=200)

                self.stop_wheel()
                self.change_color_mode("COL-REFLECT")

            if control > max_control:
                control = max_speed_bound - default
            elif control < min_control:
                control = -max_speed_bound + default

            self.right_wheel.run_forever(speed_sp=default - control)
            self.left_wheel.run_forever(speed_sp=default + control)

            current_reading = float(self.left_lower_ultrassonic)

            if(current_reading < small_read and ((self.learning_dictionary[self.DEFAULT_PIPE] - self.DEFAULT_PASSES) <= self.left_wheel.position)):
                small_read = current_reading
                default = 200
                pid.tunings = (1.025, 0, 0.9)
                closer_pipe_passes = self.left_wheel.position
                print("small read ", small_read)

        self.stop_wheel()

        if small_read > 40:
            Sound.beep()
            if self.DEFAULT_PIPE < 20:

                oldest_piper_size = self.DEFAULT_PIPE
                self.DEFAULT_PIPE += 5

                if self.learning_dictionary[oldest_piper_size] < self.learning_dictionary[self.DEFAULT_PIPE]:
                    self.init_wheel_position = self.learning_dictionary[oldest_piper_size]

                else:
                    print("entrei else")
                    self.change_color_mode('COL-COLOR')
                    self.rotate_left_90()
                    self.move_motors(100,100)
                    while self.right_color_sensor == "white" and self.left_color_sensor == "white": pass
                    self.stop_wheel()
                    self.color_alignment(["black"], self.PIPE_AREA, ["white"])
                    self.move_motors(-100,-100)
                    sleep(0.5)
                    self.stop_wheel()
                    self.rotate_left_90()
                    self.right_pid(self.INFINITY)
                    self.move_motors(-200,-200)
                    sleep(1.5)
                    self.rotate_right_90()
                    self.move_motors(100,100)
                    while (self.left_color_sensor == "white" and self.right_color_sensor == "white"):pass
                    self.stop_wheel()
                    self.color_alignment(["black"], self.PIPE_AREA, ["white"])
                    self.move_motors(-100, -100)
                    sleep(0.5)
                    self.stop_wheel()
                    self.rotate_right_90()
            return False

        actual_position = self.left_wheel.position

        if(self.DEFAULT_PIPE == 10):
            actual_position += 0

        else:
            actual_position += 0

        self.left_wheel.run_to_rel_pos(position_sp=-(actual_position - closer_pipe_passes), speed_sp=300)
        self.right_wheel.run_to_rel_pos(position_sp=-(actual_position - closer_pipe_passes), speed_sp=300)
        self.right_wheel.wait_while('running')
        self.left_wheel.wait_while('running')
        self.rotate_left_90()

        # self.gyro_reset()
        # while (self.gyro.value() > -5):
        #     self.left_wheel.run_forever(speed_sp=-500)
        #     self.right_wheel.run_forever(speed_sp=500)
        # self.stop_wheel()

        self.init_wheel_position = 0
        return True

    def failed_to_reach_the_pipe(self):
        self.move_motors(-200, -200)
        sleep(2)
        self.stop_wheel()
        self.angle_reset()
        self.change_color_mode('COL-COLOR')
        self.move_motors(-200, -200)
        while self.left_color_sensor in self.PIPE_AREA + ["black"] or self.left_color_sensor in self.PIPE_AREA + [
            "black"]: pass
        self.stop_wheel()
        self.color_alignment(["black"], self.PIPE_AREA, ["white"])
        self.stop_wheel()
        self.move_motors(-100,-100)
        sleep(0.5)
        self.stop_wheel()

    def toward_the_pipe(self):

        self.change_color_mode('COL-REFLECT')

        self.gyro_reset()
        self.motors_position_reset()
        print(self.gyro.value())
        self.stop_wheel()

        pid = PID(47, 0, 11, setpoint=0)
        default = 200
        max_speed_bound = 500

        max_control = max_speed_bound - default
        min_control = -max_speed_bound + default

        while int(self.left_color_sensor) != 0 and int(self.right_color_sensor) != 0:

            print("PID")

            left, right = self.middle_ultrasonic_sensors()
            print(left, right)


            if (left < 8 and right < 8):
                self.stop_wheel()
                Sound.beep()
                ini = time.time()
                left, right = self.middle_ultrasonic_sensors()
                pid.setpoint = 0
                pid.tunings = (20, 0, 30)
                default = 50
                max_speed_bound = 200

                while ((time.time() - ini < 2) and (left > 3 and right > 3)):
                    left, right = self.middle_ultrasonic_sensors()

                    control = pid(left - right)
                    if control > max_control:
                        control = max_speed_bound - default
                    elif control < min_control:
                        control = -max_speed_bound + default

                    self.right_wheel.run_forever(speed_sp=default + control)
                    self.left_wheel.run_forever(speed_sp=default - control)

                if (left <= 3 or right <= 3) and abs(left - right) <= 3:
                    break

            elif left == 255 and right == 255:
                break

            default = 200
            pid.tunings = (54, 0, 20)
            control = pid(left - right)

            if control > max_control:
                control = max_speed_bound - default
            elif control < min_control:
                control = -max_speed_bound + default

            self.right_wheel.run_forever(speed_sp=default + control)
            self.left_wheel.run_forever(speed_sp=default - control)

        self.stop_wheel()
        if((int(self.left_color_sensor) == 0 or int(self.right_color_sensor) == 0)):
            self.failed_to_reach_the_pipe()
            if(self.learning_dictionary[self.DEFAULT_PIPE] > 5000):
                self.rotate_right_90()
                self.left_pid(self.INFINITY)
                self.change_color_mode('COL-COLOR')
                self.move_motors(-100, -100)
                while self.left_color_sensor != 'white' and self.right_color_sensor != 'white': pass
                sleep(2)
                self.stop_wheel()
                self.rotate_left_90()

            else:
                self.rotate_left_90()
                self.right_pid(self.INFINITY)
                self.change_color_mode('COL-COLOR')
                self.move_motors(-100, -100)
                while self.left_color_sensor != 'white' and self.right_color_sensor != 'white': pass
                sleep(2)
                self.stop_wheel()
                self.rotate_right_90()

            self.move_motors(100, 100)
            while self.left_color_sensor == 'white' and self.right_color_sensor == 'white': pass
            self.stop_wheel()
            self.color_alignment(["black"], self.PIPE_AREA, ["white"])
            self.move_motors(-100, -100)
            sleep(0.5)
            self.stop_wheel()
            if (self.learning_dictionary[self.DEFAULT_PIPE] > 5000):
                self.rotate_left_90()
            else:
                self.rotate_right_90()
            return False

        self.move_motors(100,100)
        sleep(1)
        self.stop_wheel()
        return True

    def middle_ultrasonic_sensors(self):
        return self.left_ultrassonic.value() / 10, self.right_ultrassonic.value() / 10

    def test_ultrassoic(self):

        left, right = self.middle_ultrasonic_sensors()

        if(left > right):

            init_one = time.time()
            left, right = self.middle_ultrasonic_sensors()

            self.move_motors(1000,0)
            while left > right and time.time() - init_one < 3:
                left,right = self.middle_ultrasonic_sensors()
                left = int(left) + 1
            self.stop_wheel()
            print("maior left")

        elif (right > left):

            init_two = time.time()
            left, right = self.middle_ultrasonic_sensors()

            self.move_motors(0, 1000)
            while right > left and time.time() - init_two < 3:
                left, right = self.middle_ultrasonic_sensors()
                right = int(right) + 1
            self.stop_wheel()
            print("maior right")

    def verify_the_pipe_is(self):
        self.open_claws()
        self.claw_position_reset()
        self.move_motors(100,100)
        sleep(1)
        self.stop_wheel()
        return self.getting_the_pipe()

    def the_pipe_is(self):
        sum = (self.left_claw.position + self.right_claw.position)

        if(self.DEFAULT_PIPE == 10):

            if (sum > 385):
                return "lost"

            elif (sum > 345):
                return "perpendicular"

            return "parallel"

        else:
            if (sum > 385):
                return "lost"

            elif (sum > 335):
                return "perpendicular"

            return "parallel"


    def open_claws(self):
        self.left_claw.run_forever(speed_sp=-800)
        self.right_claw.run_forever(speed_sp=-800)
        sleep(1)
        self.claw_position_reset()

    def close_claws(self):
        self.claw_position_reset()
        self.left_claw.run_forever(speed_sp=600)
        self.right_claw.run_forever(speed_sp=600)
        sleep(1)

    def getting_the_pipe(self):
        self.close_claws()
        return self.the_pipe_is()

    def re_pipe(self,size):
        if(size == 10):
            self.move_motors(-200, -200)
            sleep(1.75)
            self.stop_wheel()

        elif(size == 15):
            self.move_motors(-200,-200)
            sleep(2)
            self.stop_wheel()

        self.open_claws()

    def grab_the_pipe_with_front_claw(self):
        self.move_motors(100,100)
        while max(self.middle_ultrasonic_sensors()) > 5: pass
        self.stop_wheel()

        self.move_motors(-50,-50)
        while min(self.middle_ultrasonic_sensors()) <= 14: pass
        self.stop_wheel()
        self.claw_grab()
        self.move_motors(100,100)
        init = time.time()
        while time.time() - init < 1.85: pass
        self.stop_wheel()
        self.claw_init()

    def hug_pipe(self):
        self.open_claws()
        self.claw_grab()
        sleep(3)
        self.close_claws()

    def adjust_claw(self):

        print("entrei")

        if (self.left_claw.position > self.right_claw.position):
            print("left > right")
            while self.left_claw.position - self.right_claw.position > 0:
                self.right_claw.run_forever(speed_sp=400)
                self.left_claw.run_forever(speed_sp=-400)
                print("left > right ",self.left_claw.position - self.right_claw.position)

            self.left_claw.stop()
            self.right_claw.stop()

        elif (self.left_claw.position < self.right_claw.position):
            while - self.left_claw.position + self.right_claw.position > 0:
                self.right_claw.run_forever(speed_sp=-400)
                self.left_claw.run_forever(speed_sp=400)
                print("right > left ", self.left_claw.position - self.right_claw.position)

            self.left_claw.stop()
            self.right_claw.stop()

    def rotate(self, angle, speed):
        self.gyro_reset()
        if(angle > 0):
            self.move_motors(speed,-speed)
            while self.gyro.value() < angle: pass
            self.stop_wheel()
        else:
            self.move_motors(-speed, speed)
            while self.gyro.value() > angle: pass
            self.stop_wheel()

    def from_the_hole_case(self):
        self.angle_reset()
        self.rotate(180,300)
        self.adjust_claw()
        self.open_claws()
        self.grab_the_pipe_with_front_claw()
        self.stop_wheel()

    def from_the_border_case(self):

        self.stop_wheel()
        self.angle_reset()
        self.adjust_claw()
        self.close_claws()

        self.change_color_mode('COL-COLOR')

        if (self.DEFAULT_PIPE == 10):
            self.move_motors(200, 200)
            while (self.left_color_sensor in (self.PIPE_AREA + ["black"])) or (
                    self.right_color_sensor in self.PIPE_AREA + ["black"]): pass
            self.stop_wheel()
            self.color_alignment(["black"], ["white"], self.PIPE_AREA)
            self.rotate(180,300)

        self.move_motors(-200, -200)
        while (self.left_color_sensor in (self.PIPE_AREA + ["black"])) or (
                self.right_color_sensor in self.PIPE_AREA + ["black"]): pass
        self.stop_wheel()
        self.color_alignment(["black"],self.PIPE_AREA, ["white"])

        self.re_pipe(self.DEFAULT_PIPE)

        self.move_motors(-300, -300)
        sleep(1)

        if self.learning_dictionary[self.DEFAULT_PIPE] < 5000:

            self.stop_wheel()
            self.rotate_right_90()

            self.move_motors()
            sleep(2)
            self.stop_wheel()
            self.rotate_left_90()

            self.move_motors()
            while self.right_color_sensor == "white" and self.left_color_sensor == "white": pass
            self.stop_wheel()
            self.color_alignment(["black"], self.PIPE_AREA, ["white"])
            self.move_motors(-100, -100)
            sleep(0.5)
            self.stop_wheel()
            self.rotate_left_90()
            self.right_pid(distance= 800,claw_grab = True)
            self.rotate_left_90()


        else:
            self.stop_wheel()
            self.rotate_left_90()

            self.move_motors()
            sleep(2)
            self.stop_wheel()
            self.rotate_right_90()

            self.move_motors()
            while self.right_color_sensor == "white" and self.left_color_sensor == "white": pass
            self.stop_wheel()
            self.color_alignment(["black"], self.PIPE_AREA, ["white"])
            self.move_motors(-100, -100)
            sleep(0.5)
            self.stop_wheel()
            self.rotate_right_90()
            self.left_pid(distance=800, claw_grab=True)
            self.rotate_right_90()

    def grab_the_pipe(self):
        self.move_motors(-75,-75)
        sleep(1)
        self.stop_wheel()
        self.close_claws()

        if(self.DEFAULT_PIPE != 10):

            pipe_aligment = self.the_pipe_is()
            print(pipe_aligment)
            print(self.left_claw.position + self.right_claw.position)

            if(pipe_aligment == 'lost'):
                pass
            elif(pipe_aligment == 'parallel'):
                self.from_the_hole_case()
            else:
                self.from_the_border_case()

        else:
            self.from_the_hole_case()
            self.move_motors(-50,-50)
            sleep(1)
            self.stop_wheel()

            left,right = self.middle_ultrasonic_sensors()

            self.change_color_mode('COL-COLOR')
            print(self.middle_ultrasonic_sensors())

            if(left > 10 and right > 10):
                self.move_motors(200,200)
                while (self.left_color_sensor in self.PIPE_AREA or self.right_color_sensor in self.PIPE_AREA):pass
                self.stop_wheel()
                self.color_alignment(["black"], ["white"],self.PIPE_AREA)
                self.move_motors()
                sleep(1.5)
                self.stop_wheel()
                self.rotate(180,300)
                #supondo que o cano foi pego

            else:
                self.move_motors(100,100)
                left, right = self.middle_ultrasonic_sensors()
                while left > 5 and right > 5: left,right = self.middle_ultrasonic_sensors()

                sleep(1)
                self.stop_wheel()

                self.close_claws()
                self.from_the_border_case()

    def prepare_to_dive(self):
        self.change_color_mode('COL-REFLECT')
        self.move_motors(-200,-200)
        while int(self.right_color_sensor) == 0 or int(self.left_color_sensor) == 0:pass
        sleep(2)
        self.stop_wheel()
        self.rotate(-70,300)

    def test_adjust_claw(self):
        self.open_claws()
        sleep(1)
        self.claw_position_reset()
        self.close_claws()


        self.adjust_claw()
        self.move_motors(-25,-25)
        sleep(2)
        self.stop_wheel()

        self.left_claw.stop()
        self.right_claw.stop()
        while 1:
            print(self.left_claw.position, self.right_claw.position)

    def pipeline_support_following(self):
        self.stop_wheel()
        print("pipeline_support_following")
        default_speed_for_pipeline = 150
        max_control_for_pipeline = 300
        pid = PID(10, 0, 2,
                  setpoint=4)
        self.change_color_mode('COL-REFLECT')

        while True:
            print(self.left_color_sensor, self.right_color_sensor)
            side_distance = self.infrared.value()
            control = pid(side_distance)
            color_data = [self.left_color_sensor, self.right_color_sensor]

            if int(color_data[0]) == 0 or int(color_data[1]) == 0:
                self.stop_wheel()
                print("finished pipeline_support_following")
                # self.color_alignment(aligment_with_color=True)
                self.move_motors(-500, -500)
                sleep(0.5)
                self.stop_wheel()
                self.rotate(-85,300)
                return

            if max(self.middle_ultrasonic_sensors()) <= self.WALL_DISTANCE:
                self.stop_wheel()
                self.rotate_right_90()

            if control > max_control_for_pipeline:
                control = max_control_for_pipeline
            elif control < -max_control_for_pipeline:
                control = -max_control_for_pipeline

            speed_a = default_speed_for_pipeline + control
            speed_b = default_speed_for_pipeline - control

            self.left_wheel.run_forever(speed_sp=speed_a)
            self.right_wheel.run_forever(speed_sp=speed_b)

    def phase_out_place_pipe(self, hole_size):
        k_steps = 230
        kp_for_pipeline = 6
        ki_for_pipeline = 0
        kd_for_pipeline = 2
        set_point_for_pipeline = 8
        default_speed_for_pipeline = 150
        max_control_for_pipeline = 300
        front_distance_to_rotate = 2

        self.stop_wheel()
        print("called phase_out_place_pipe")

        pid = PID(kp_for_pipeline, ki_for_pipeline, kd_for_pipeline,
                  setpoint=set_point_for_pipeline)

        if hole_size == 10:
            k_steps = 230

        elif hole_size == 15:
            k_steps = 360 - 120

        elif hole_size == 20:
            k_steps = 480 - 140

        initial_step = self.left_wheel.position + self.right_wheel.position
        while self.left_wheel.position + self.right_wheel.position <= initial_step + k_steps * 2:

            # verifica colisão frontal
            if min(self.middle_ultrasonic_sensors()) >= 7.5:
                self.stop_wheel()
                print("robot found wall")
                break

            # verifica queda
            color_data = [self.left_color_sensor,self.right_color_sensor]
            if color_data[0] == 0 or color_data[1] == 0:
                self.stop_wheel()
                break

            control = pid(self.infrared.value())

            if control > max_control_for_pipeline:
                control = max_control_for_pipeline
            elif control < -max_control_for_pipeline:
                control = -max_control_for_pipeline

            speed_a = default_speed_for_pipeline + control
            speed_b = default_speed_for_pipeline - control

            self.left_wheel.run_forever(speed_sp=speed_a)
            self.right_wheel.run_forever(speed_sp=speed_b)

        self.stop_wheel()
        return

    def go_up_to_meeting_area(self):
        self.change_color_mode('COL-COLOR')
        self.move_motors(-1000,-1000)
        while self.left_color_sensor != 'white' or self.right_color_sensor != 'white' : pass
        self.stop_wheel()
        self.rotate(180,self.DEFAULT_SPEED)

    def go_down_to_pipeline(self):
        self.change_color_mode('COL-COLOR')
        self.move_motors(-1000,-1000)
        while self.left_color_sensor != 'blue' or self.right_color_sensor != 'blue': pass
        self.stop_wheel()

        while not (self.green_alignment()): pass

        self.green_area_PID()


    def green_area_PID(self):
        self.change_color_mode('COL-REFLECT')
        default = 200
        pid = PID(3, 0, 6, setpoint=13)

        max_speed_bound = 300
        max_control = max_speed_bound - default
        min_control = -max_speed_bound + default

        while int(self.left_color_sensor) != 0 and int(self.right_color_sensor) != 0:
            control = pid(self.infrared.value())

            if control > max_control:
                control = max_speed_bound - default
            elif control < min_control:
                control = -max_speed_bound + default

            self.right_wheel.run_forever(speed_sp=default - control)
            self.left_wheel.run_forever(speed_sp=default + control)

        self.stop_wheel()
        self.move_motors(-300,-300)
        while (int(self.left_color_sensor) == 0 or int(self.right_color_sensor) == 0 ): pass
        sleep(0.5)
        self.stop_wheel()
        self.rotate_right_90()
        self.prepare_to_pipeline_following()

    def prepare_to_pipeline_following(self):
        self.move_motors(200,200)
        while max(self.middle_ultrasonic_sensors()) >= self.WALL_DISTANCE: pass
        self.rotate_right_90()

    def green_alignment(self):
        self.gyro_reset()

        self.change_color_mode('COL-COLOR')
        self.move_motors(200,200)
        while self.right_color_sensor == 'blue' and self.left_color_sensor == 'blue':pass
        self.stop_wheel()

        self.move_motors(0,200)
        while self.right_color_sensor == 'blue':
            if (self.gyro.value()) < -70:
                self.stop_wheel()
                self.angle_reset()
                return False
        self.stop_wheel()

        self.move_motors(200,0)
        while self.left_color_sensor == 'blue':
            if (self.gyro.value()) > 70:
                self.stop_wheel()
                self.angle_reset()
                return False

        self.stop_wheel()
        self.move_motors(-400,-400)
        sleep(0.5)
        self.stop_wheel()
        self.rotate_right_90()
        return True