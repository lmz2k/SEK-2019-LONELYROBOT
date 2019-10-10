#!/usr/bin/env python3
from teste import *

#
# left_wheel_motor.run_forever(speed_sp = 1000)
# right_wheel_motor.run_forever(speed_sp = 1000)
#
# sleep(15)
#
# left_wheel_motor.run_forever(speed_sp = -1000)
# right_wheel_motor.run_forever(speed_sp = -1000)
#
# sleep(15)
#
# left_wheel_motor.stop()
# right_wheel_motor.stop()

# left_wheel_motor.run_forever(speed_sp=-1000)
# right_wheel_motor.run_forever(speed_sp=-1000)
# sleep(2)
#
# ini = time.time()
#
# while time.time() - ini < 3:
#
#     left_wheel_motor.run_forever(speed_sp=-300)
#     right_wheel_motor.run_forever(speed_sp=-1000)
#     sleep(0.25)
#     left_wheel_motor.run_forever(speed_sp=-1000)
#     right_wheel_motor.run_forever(speed_sp=-300)
#     sleep(0.25)

left_wheel_motor.run_forever(speed_sp=1000)
right_wheel_motor.run_forever(speed_sp=1000)
sleep(2)

left_wheel_motor.stop()
right_wheel_motor.stop()