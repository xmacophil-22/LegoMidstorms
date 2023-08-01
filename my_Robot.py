#!/usr/bin/env python3
import multiprocessing as m
from math import inf
from time import sleep, time
from ev3dev2.motor import OUTPUT_A as ENGINE_RIGHT_OUTPUT
from ev3dev2.motor import OUTPUT_D as ENGINE_LEFT_OUTPUT
from ev3dev2.motor import OUTPUT_C as ENGINE_BALL_OUTPUT

from ev3dev2.motor import SpeedPercent, MoveTank, LargeMotor
from ev3dev2.sensor import INPUT_1 as LIGHT_INPUT_SENSOR_RIGHT
from ev3dev2.sensor import INPUT_2 as ULTRA_INPUT
from ev3dev2.sensor import INPUT_4 as LIGHT_INPUT_SENSOR_LEFT

from ev3dev2.sensor.lego import LightSensor, ColorSensor, UltrasonicSensor
from parameters import initialization


class Robot:
    def __init__(self):
        self = initialization(self)

        # initialization of Motors:
        self.BALL_ENGINE = LargeMotor(ENGINE_BALL_OUTPUT)
        self.TANK = MoveTank(ENGINE_LEFT_OUTPUT, ENGINE_RIGHT_OUTPUT)
        self.ENGINE_LEFT = LargeMotor(ENGINE_LEFT_OUTPUT)
        self.ENGINE_RIGHT = LargeMotor(ENGINE_RIGHT_OUTPUT)

        # initalization of Sensors:
        self.LIGHT_SENSOR_LEFT = LightSensor(LIGHT_INPUT_SENSOR_LEFT)
        self.LIGHT_SENSOR_RIGHT = LightSensor(LIGHT_INPUT_SENSOR_RIGHT)
        self.LIGHT_SENSOR_MIDDLE = ColorSensor()
        self.LIGHT_SENSOR_MIDDLE.mode = 'COL-REFLECT'
        self.ULTRA = UltrasonicSensor(ULTRA_INPUT)
        self.ULTRA.MODE = 'US-DIST-CM'

    def light_sensor_on_white(self, sensor: LightSensor) -> bool:
        return sensor.reflected_light_intensity > self.MIN_LIGHT_WHITE

    def read_ultra(self):
        units = self.ULTRA.units
        distance = self.ULTRA.value() / 10  # convert mm to cm
        print(str(distance) + " " + units)

    def stop_distance_reached(self):
        if self.ULTRA.value() / 10 < self.STOP_DISTANCE:
            return True
        return False

    def is_on_white(self):
        return self.LIGHT_SENSOR_MIDDLE.value() > 10

    def accelerate(self):
        new_speed = self.CURRENT_SPEED * self.ACCELERATION
        if time() - self.FORWARD_TIME > self.ACCELERATION_INTERVAl and new_speed < self.MAX_ACCELERATION_SPEED:
            self.CURRENT_SPEED = new_speed
            self.TANK.on(SpeedPercent(self.CURRENT_SPEED), SpeedPercent(self.CURRENT_SPEED))

    def scan_code(self):
        if (self.is_on_white() and self.IS_LAST_STEP_BLACK or not self.is_on_white() and not self.IS_LAST_STEP_BLACK):
            self.STEPS_COUNTED += 1
            self.IS_LAST_STEP_BLACK = not self.IS_LAST_STEP_BLACK
            if (self.STEPS_COUNTED == 6):
                return True
            self.TIME_PASSED = time()
        elif (time() - self.TIME_PASSED > self.MAX_TIME_PASSED and self.STEPS_COUNTED < 6):
            self.STEPS_COUNTED = 0
            self.TIME_PASSED = 0
        return False


def calibrate_sensors(robby):
    while 1:
        print("middle:", round(robby.LIGHT_SENSOR_MIDDLE.value(), 2), end="")
        print(" left:", round(robby.LIGHT_SENSOR_LEFT.reflected_light_intensity, 2), end="")
        print(" right:", round(robby.LIGHT_SENSOR_RIGHT.reflected_light_intensity), 2)
        sleep(1)


def calibrate_ultra(robby):
    while 1:
        robby.read_ultra()