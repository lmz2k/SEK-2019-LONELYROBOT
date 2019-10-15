import paho.mqtt.client as mqtt
from ev3dev.ev3 import *
from time import sleep
from simple_pid import *

DEFAULT_SPEED = 500

class Robot():

    def __init__(self):

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
        self.upper_front_ultrassonic = UltrasonicSensor('in2')
        self.gyro = GyroSensor('in1')

        self.upper_front_ultrassonic.mode = 'US-DIST-CM'
        self.left_ultrassonic.mode = 'US-DIST-CM'
        self.right_ultrassonic.mode = 'US-DIST-CM'
        self.gyro.mode = 'GYRO-ANG'

        ##Secondary Brick

        self.left_color_sensor = "None"
        self.right_color_sensor = "None"

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

        ##OTHERS

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
        return self.left_color_sensor,self.right_color_sensor,self.left_lower_ultrassonic

    def tertiary_brick_values(self):
        return self.left_infrared,self.right_infrared,self.left_upper_ultrassonic

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
                self.move_motors(-200, -200)
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

            if self.right_wheel.position > 200 and entrar:
                entrar = False
                self.gyro_reset()
                default = 300
                pid.tunings = (1.025, 0, 0.9)
                if (claw_grab):
                    self.claw_grab()

            if(self.upper_front_ultrassonic.value() / 10 > 30):
                default = 200
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

            if control > max_control:
                control = max_speed_bound - default
            elif control < min_control:
                control = -max_speed_bound + default

            self.right_wheel.run_forever(speed_sp=default + control)
            self.left_wheel.run_forever(speed_sp=default - control)

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
            if self.left_wheel.position > 200 and entrar:
                entrar = False
                self.gyro_reset()
                default = 300
                pid.tunings = (1.025, 0, 0.13)
                if (claw_grab):
                    self.claw_grab()

            if (self.upper_front_ultrassonic.value() / 10 > 30):
                default = 200
                pid.tunings = (1.025, 0, 0.9)

            if (self.gyro.value() < -25):

                self.stop_wheel()
                self.change_color_mode("COL-COLOR")

                while self.left_color_sensor in self.PIPE_AREA:
                    self.move_motors(-200,-200)
                self.stop_wheel()

                while self.left_color_sensor == "white":
                    self.move_motors(200,200)
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
        self.move_motors(-200,-200)
        sleep(2)
        self.stop_wheel()

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

        self.move_motors(-200,-200)
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

        self.move_motors(-200, -200)
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
        self.move_motors(-200, -200)
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

            if (self.upper_front_ultrassonic.value() / 10 > 30):
                default = 200
                pid.tunings = (1.025, 0, 0.9)

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
                    self.move_motors(-200,-200)
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
                    self.move_motors(-200, -200)
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

    def get_closer_with_the_pipe(self):


        self.move_motors(-170,-170)
        sleep(1)

        self.claw_grab()
        ini = time.time()
        while time.time() - ini <= 3:
            self.move_motors(200, 200)


        self.stop_wheel()

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
        self.move_motors(-200,-200)
        sleep(0.5)
        self.stop_wheel()

    def toward_the_pipe(self):

        self.change_color_mode('COL-REFLECT')

        self.gyro_reset()
        self.motors_position_reset()
        print(self.gyro.value())
        self.stop_wheel()

        pid = PID(47, 0, 14, setpoint=0)
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
            self.move_motors(-200, -200)
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

        if (sum > 385):
            return "lost"

        elif (sum > 345):
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
        sleep(2)

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

    # def toward_the_pipe(self):
    #     self.gyro_reset()
    #     self.motors_position_reset()
    #     print(self.gyro.value())
    #     self.stop_wheel()
    #
    #     pid = PID(54, 0, 20, setpoint=0)
    #     default = 300
    #     max_speed_bound = 500
    #     max_control = max_speed_bound - default
    #     min_control = -max_speed_bound + default
    #
    #
    #     while True:
    #
    #         left, right = self.middle_ultrasonic_sensors()
    #         print(left,right)
    #
    #
    #         if (left < 8 and right < 8):
    #
    #             Sound.beep()
    #             ini = time.time()
    #             left, right = self.middle_ultrasonic_sensors()
    #
    #             pid.setpoint = 0
    #             pid.tunings = (65, 0, 30)
    #             default = 50
    #
    #
    #             while ((time.time() - ini < 2) and (left > 3 or right > 3)):
    #                 left, right = self.middle_ultrasonic_sensors()
    #
    #                 control = pid(left - right)
    #                 if control > max_control:
    #                     control = max_speed_bound - default
    #                 elif control < min_control:
    #                     control = -max_speed_bound + default
    #
    #                 self.right_wheel.run_forever(speed_sp=default + control)
    #                 self.left_wheel.run_forever(speed_sp=default - control)
    #
    #
    #             if (left <= 3 or right <= 3) and  abs(left-right) <= 3:
    #                 break
    #
    #
    #             break
    #
    #         elif left == 255 and right == 255:
    #                 break
    #
    #         default = 200
    #         pid.tunings = (54, 0, 20)
    #         control = pid(left-right)
    #
    #         if control > max_control:
    #             control = max_speed_bound - default
    #         elif control < min_control:
    #             control = -max_speed_bound + default
    #
    #         self.right_wheel.run_forever(speed_sp=default + control)
    #         self.left_wheel.run_forever(speed_sp=default - control)
    #
    #     self.stop_wheel()
    #     self.move_motors(50,50)
    #     sleep(0.5)
    #     self.stop_wheel()

    def hug_pipe(self):
        self.open_claws()
        self.claw_grab()
        sleep(3)
        self.close_claws()

    # def toward_the_pipe(self):
    #
    #     self.gyro_reset()
    #     self.motors_position_reset()
    #     print(self.gyro.value())
    #     self.stop_wheel()
    #
    #     pid = PID(47, 0, 14, setpoint=0)
    #     default = 200
    #     max_speed_bound = 500
    #
    #     max_control = max_speed_bound - default
    #     min_control = -max_speed_bound + default
    #
    #     while True:
    #
    #         left, right = self.middle_ultrasonic_sensors()
    #         print(left, right)
    #
    #
    #         if (left < 8 and right < 8):
    #             self.stop_wheel()
    #             Sound.beep()
    #             ini = time.time()
    #             left, right = self.middle_ultrasonic_sensors()
    #
    #             pid.setpoint = 0
    #             pid.tunings = (20, 0, 30)
    #             default = 50
    #
    #             while ((time.time() - ini < 2) and (left > 3 or right > 3)):
    #                 left, right = self.middle_ultrasonic_sensors()
    #
    #                 control = pid(left - right)
    #                 if control > max_control:
    #                     control = max_speed_bound - default
    #                 elif control < min_control:
    #                     control = -max_speed_bound + default
    #
    #                 self.right_wheel.run_forever(speed_sp=default + control)
    #                 self.left_wheel.run_forever(speed_sp=default - control)
    #
    #             if (left <= 3 or right <= 3) and abs(left - right) <= 3:
    #                 break
    #
    #             break
    #         elif left == 255 and right == 255:
    #             break
    #
    #         default = 200
    #         pid.tunings = (54, 0, 20)
    #         control = pid(left - right)
    #
    #         if control > max_control:
    #             control = max_speed_bound - default
    #         elif control < min_control:
    #             control = -max_speed_bound + default
    #
    #         self.right_wheel.run_forever(speed_sp=default + control)
    #         self.left_wheel.run_forever(speed_sp=default - control)

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
            # while 1:
            #     print(left_claw_motor.position, right_claw_motor.position)

        elif (self.left_claw.position < self.right_claw.position):
            while - self.left_claw.position + self.right_claw.position > 0:
                self.right_claw.run_forever(speed_sp=-400)
                self.left_claw.run_forever(speed_sp=400)
                print("right > left ", self.left_claw.position - self.right_claw.position)

            self.left_claw.stop()
            self.right_claw.stop()

        self.move_motors(-25, -25)
        sleep(2)
        self.stop_wheel()

    def from_the_hole_case(self):
        self.angle_reset()
        self.adjust_claw()
        self.close_claws()

        self.open_claws()

        self.move_motors(-200, -200)
        sleep(1)
        self.stop_wheel()

        self.claw_grab()
        sleep(1)

        self.move_motors(200, 200)
        sleep(2)
        self.stop_wheel()

    def from_the_border_case(self):

        self.move_motors(-200, -200)
        sleep(1)
        self.stop_wheel()
        self.angle_reset()
        self.adjust_claw()
        self.close_claws()

        self.move_motors(-200, -200)
        self.change_color_mode('COL-COLOR')
        while (self.left_color_sensor in (self.PIPE_AREA + ["black"])) or (
                self.right_color_sensor in self.PIPE_AREA + ["black"]): pass

        self.stop_wheel()
        self.color_alignment(["black"], self.PIPE_AREA, ["white"])
        self.re_pipe(self.DEFAULT_PIPE)

        self.move_motors(-200, -200)
        sleep(1.5)

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
            self.move_motors(-200, -200)
            sleep(0.5)
            self.stop_wheel()
            self.rotate_left_90()
            self.right_pid(distance= 800,claw_grab = True)

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
            self.move_motors(-200, -200)
            sleep(0.5)

            self.rotate_right_90()
            self.left_pid(distance= 800,claw_grab = True)

    def grab_the_pipe(self):
        self.move_motors(-50,-50)
        sleep(1.25)
        self.stop_wheel()
        self.close_claws()

        if(self.DEFAULT_PIPE != 10):

            pipe_aligment = self.the_pipe_is()
            print(pipe_aligment)
            print(self.left_claw.position + self.right_claw.position)

        # pipe_aligment = self.verify_the_pipe_is()
        #
        # x = input()
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
                self.move_motors(-200,-200)
                while (self.left_color_sensor in self.PIPE_AREA or self.right_color_sensor in self.PIPE_AREA):pass
                self.stop_wheel()
                self.color_alignment(["black"], self.PIPE_AREA, ["white"])
                self.move_motors(-200, -200)
                sleep(0.5)
                self.stop_wheel()
                self.rotate_left_90()

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
        if(self.learning_dictionary[self.DEFAULT_PIPE] == 1600):

            self.rotate_right_90()
            self.color_alignment(["black"], self.PIPE_AREA, ["white"])
            self.move_motors(-200,-200)
            sleep(0.5)
            self.stop_wheel()
            self.rotate_right_90()

        self.left_pid(self.INFINITY)

        self.move_motors(-200,-200)
        while int(self.right_color_sensor) == 0 or int(self.left_color_sensor) == 0:pass
        sleep(2)
        self.stop_wheel()
        self.rotate_right_90()

    def test_diving(self):
        self.move_motors(-800,-800)
        sleep(1.3)
        Sound.beep()
        self.rotate_left_90()

        Sound.beep()

        self.move_motors(0, 1000)
        sleep(5)

        self.stop_wheel()

        # self.move_motors(-200, -800)
        # sleep(0.3)
        # self.move_motors(500, 1000)
        # sleep(0.5)
        # self.move_motors(1000, 1000)
        # sleep(2)
        # self.stop_wheel()
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


