#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.nxtdevices import (LightSensor)
from pybricks.media.ev3dev import SoundFile, ImageFile
import random 

ev3 = EV3Brick()
left_motor = Motor(Port.D,Direction.COUNTERCLOCKWISE)
right_motor = Motor(Port.A,Direction.COUNTERCLOCKWISE)
light_sensor = LightSensor(Port.S2)
sonic_sensor = UltrasonicSensor(Port.S4) 
color_sensor = ColorSensor(Port.S3)

#This is for various states 
robot_wandering = True # This means that the goal has not been found yet 
following_wall = False # We are currently following the wall 
goal_clearing = False # We have located the goal now we are clearing the goal 
goal_found = False # Goal found is initially set to zero 

# Since our robot is at the blue line currently, moving it until blue line is avoided
def back_up(value, side):
    if side == 0:
        right_motor.run(-value-20)
        while light_sensor.reflection() < 15:
                pass
        right_motor.stop()
    elif side == 1:
        right_motor.run(value)
        while color_sensor.color() == Color.BLUE:
                pass
        right_motor.stop()

def goal_finding():
    # This means that we found the goal 
    global goal_found
    if color_sensor.color() == Color.RED:
        right_motor.stop()
        left_motor.stop()
        goal_found = True # Found the goal 
        ev3.speaker.say("Goal state found")
        return True 
    
    return False

def wander():
    while light_sensor.reflection() > 15:
        left_motor.run(150)
        right_motor.run(random.randint(130,140))
        # This means that we found the goal 
        if goal_finding():
            return True
    right_motor.stop()
    left_motor.stop()
    ev3.speaker.say("Blue wall found")
    return False # Found a wall

def bounce(no_of_bounces):
    # Since we are still at blue line
    right_motor.run_time(-100,random.randint(300,2400)) # Turns the robot away from the wall
    # Maximum is 90 degree min is about 15 degrees
    
    counter = 0
    while no_of_bounces > counter:
        back_up(100, 0)
        # Then moves in a straight line 
        right_motor.run(150)
        left_motor.run(150)

        blue_line_counter = 0

        # Until blue is not found 
        while light_sensor.reflection() > 15: # Will move till blue is found 
            if color_sensor.color() == Color.BLUE:
                blue_line_counter += 1
            if blue_line_counter >= 15: # threshold, may need to INCREASE based on how bad board is
                break
            # This means that we found the goal, checks while bouncing 
            if goal_finding():
                return True
            pass
        
        # Stopping both motors 
        right_motor.stop()
        left_motor.stop()  

        if blue_line_counter >= 15:
            back_up(-100, 1)
            right_motor.run_time(100,2400)
        else:
            # We found blue, lets turn 90
            right_motor.run_time(-100,2400)
        counter += 1 # Counts the number of bounces 
        

    # Currently we are 90 away from the wall; turning the robot back to the wall 
    right_motor.run_time(100,2400)
    return False # Found a wall and now starting wall following 

def wall_following(no_of_flips): # No of turns is the number of times it wiggles 
    counter = 0
    another_counter = 0
    left_motor_running_value = 25
    
    # Moves the right_motor to the blue line as we are now away from the blue line
    def move_to_blue_line():
        right_motor.run(100)
        # To count the number of turns
        while light_sensor.reflection() > 15:
            pass
        right_motor.stop()
        
    while counter <= no_of_flips:
        left_motor.run(left_motor_running_value) # This is to move the robot forward        
        back_up(100, 0)
        move_to_blue_line()
        counter += 1
    return False

def clearing():
    # may want to turn until both sensors touch red.
    # left_motor.run(100) 
    # > 70 is red 
    left_motor.run(100) 
    while (color_sensor.color() == Color.RED):
        if light_sensor.reflection() < 70:
            pass
        else:
            break
    right_motor.run(100)
    wait(7500)
    left_motor.stop()
    right_motor.stop()
    ev3.speaker.beep()

wander() # First will wander till the robot is found 

while goal_found == False: # Repeats wall following and 
    if wall_following(400): # 25 flips per tile moving 5 tiles 
        break
    if bounce(10): # Will bounce 5 times after this 
        break
    # Repeats until the goal is found 
wait(1000)
# Goal is found, now need to clear it 
clearing()

# while True:
#     print(light_sensor.reflection())
#     print(color_sensor.color())
#     wait(1000)
