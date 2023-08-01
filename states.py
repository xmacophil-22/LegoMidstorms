from my_Robot import *


class State:
    def __post_init__(self):
        pass

    def __init__(self, robby) -> None:
        self.robby = robby
        self.__post_init__()

    def next_state(self):
        return self

    def be_vocal(self):
        print(type(self))


class Movement(State):
    def __init__(self, robby, break_method=None) -> None:
        super().__init__(robby)
        self.break_method = break_method

    def next_state(self):
        if self.break_method is not None:
            return self.break_method()
        if self.robby.stop_distance_reached():
            self.robby.TANK.on(0, 0)
            self.robby.ULTRA_SENSOR_COUNTER += 1
            if self.robby.ULTRA_SENSOR_COUNTER == 1:
                return Turn_Around(self.robby)
            if self.robby.ULTRA_SENSOR_COUNTER == 2:
                return Gate(self.robby)
            if self.robby.ULTRA_SENSOR_COUNTER == 3 and time() - self.robby.GATE_TIME > 5:
                return Throw_Ball(self.robby)
        if self.robby.scan_code():
            return Recognized_Code(self.robby)
        return None


class Left(Movement):
    def __post_init__(self):
        self.robby.TANK.on(SpeedPercent(self.robby.BREAK_SPEED), SpeedPercent(self.robby.TURN_SPEED))
        self.robby.CURRENT_SPEED = self.robby.DEFAULT_SPEED
        self.robby.FORWARD_TIME = 0

    def next_state(self):
        state = super().next_state()
        if state is not None:
            return state
        if self.robby.light_sensor_on_white(self.robby.LIGHT_SENSOR_LEFT) or not self.robby.light_sensor_on_white(self.robby.LIGHT_SENSOR_RIGHT) and not self.robby.is_on_white():
            return Foreward(self.robby, self.break_method)
        return self


class Right(Movement):
    def __post_init__(self):
        self.robby.TANK.on(SpeedPercent(self.robby.TURN_SPEED), SpeedPercent(self.robby.BREAK_SPEED))
        self.robby.CURRENT_SPEED = self.robby.DEFAULT_SPEED
        self.robby.FORWARD_TIME = 0

    def next_state(self):
        state = super().next_state()
        if state is not None:
            return state
        if self.robby.light_sensor_on_white(self.robby.LIGHT_SENSOR_RIGHT) or not self.robby.light_sensor_on_white(self.robby.LIGHT_SENSOR_LEFT) and not self.robby.is_on_white():
            return Foreward(self.robby, self.break_method)
        return self


class Foreward(Movement):
    def __post_init__(self):
        self.robby.TANK.on(SpeedPercent(self.robby.CURRENT_SPEED), SpeedPercent(self.robby.CURRENT_SPEED))

    def next_state(self):
        state = super().next_state()
        if state is not None:
            return state
        if (not self.robby.light_sensor_on_white(self.robby.LIGHT_SENSOR_LEFT)) and (self.robby.light_sensor_on_white(self.robby.LIGHT_SENSOR_RIGHT) or self.robby.is_on_white()):
            return Left(self.robby, self.break_method)
        if (not self.robby.light_sensor_on_white(self.robby.LIGHT_SENSOR_RIGHT)) and (self.robby.light_sensor_on_white(self.robby.LIGHT_SENSOR_LEFT) or self.robby.is_on_white()):
            return Right(self.robby, self.break_method)
        return self


class Recognized_Code(State):
    def __post_init__(self):
        self.robby.TANK.on_for_rotations(SpeedPercent(20), SpeedPercent(20), 0.3)
        self.robby.TANK.on_for_rotations(SpeedPercent(20), SpeedPercent(20 * -1), 0.8)

    def next_state(self):
        return Push(self.robby)


class Push(State):
    def __post_init__(self):
        self.robby.SAVE_DISTANCE = self.robby.STOP_DISTANCE
        self.robby.STOP_DISTANCE = 6

    def next_state(self):
        return Foreward(self.robby, self.push_finished)

    def push_finished(self):
        if self.robby.ULTRA.value() / 10 < self.robby.STOP_DISTANCE and self.robby.ULTRA_SENSOR_COUNTER_PUSH == 0:
            self.robby.ULTRA_SENSOR_COUNTER_PUSH += 1
        elif self.robby.ULTRA.value() / 10 > 10 and self.robby.ULTRA_SENSOR_COUNTER_PUSH == 1:
            self.robby.ULTRA_SENSOR_COUNTER_PUSH += 1
            return Turn_Around(self.robby, Foreward(self.robby, self.go_back_finished))
        return None

    def go_back_finished(self):
        if not self.robby.is_on_white():
            self.robby.PUSH_TIME_FRONT_ON_WHITE = time()
        elif self.robby.light_sensor_on_white(self.robby.LIGHT_SENSOR_LEFT) and self.robby.light_sensor_on_white(self.robby.LIGHT_SENSOR_RIGHT) and time() - self.robby.PUSH_TIME_FRONT_ON_WHITE > self.robby.MIN_TIME_WHITE:
            self.robby.TANK.on_for_rotations(SpeedPercent(20 * -1), SpeedPercent(20), 0.2)
            still_on_white = self.robby.is_on_white() and self.robby.light_sensor_on_white(self.robby.LIGHT_SENSOR_LEFT) and self.robby.light_sensor_on_white(self.robby.LIGHT_SENSOR_RIGHT)
            self.robby.TANK.on_for_rotations(SpeedPercent(20), SpeedPercent(20 * -1), 0.2)
            if still_on_white:
                self.robby.TANK.on_for_rotations(SpeedPercent(20), SpeedPercent(20 * -1), 0.2)
                still_on_white = self.robby.is_on_white() and self.robby.light_sensor_on_white(self.robby.LIGHT_SENSOR_LEFT) and self.robby.light_sensor_on_white(self.robby.LIGHT_SENSOR_RIGHT)
                self.robby.TANK.on_for_rotations(SpeedPercent(20 * -1), SpeedPercent(20), 0.2)
                if still_on_white:
                    self.robby.TANK.on_for_rotations(SpeedPercent(20), SpeedPercent(20 * -1), 0.8)
                return Foreward(self.robby)
            self.robby.PUSH_TIME_FRONT_ON_WHITE = time()
        return None


class Throw_Ball(State):
    def __post_init__(self):
        self.robby.BALL_ENGINE.on_for_rotations(SpeedPercent(20), 0.4)
        self.robby.BALL_ENGINE.on_for_rotations(SpeedPercent(-7), 0.4)

    def next_state(self):
        return End(self.robby)


class Gate(State):
    def __post_init__(self):
        sleep(0.2)
        while self.robby.stop_distance_reached():
            sleep(0.4)
        self.robby.STOP_DISTANCE = 6
        self.robby.GATE_TIME = time()
        self.robby.TANK.on(SpeedPercent(self.robby.CURRENT_SPEED), SpeedPercent(self.robby.CURRENT_SPEED))

    def next_state(self):
        return Foreward(self.robby)


class Turn_Around(State):
    def __init__(self, robby, next_state=None) -> None:
        super().__init__(robby)
        self.next_state_given = next_state

    def __post_init__(self):
        self.robby.TANK.on_for_rotations(SpeedPercent(self.robby.CURRENT_SPEED * -1), SpeedPercent(self.robby.CURRENT_SPEED * -1), 1)
        self.robby.TANK.on_for_rotations(SpeedPercent(20), SpeedPercent(20 * -1), 2)
        self.robby.TANK.on(SpeedPercent(self.robby.CURRENT_SPEED), SpeedPercent(self.robby.CURRENT_SPEED))
        self.robby.STOP_DISTANCE = 15

    def next_state(self):
        if self.next_state_given is not None:
            return self.next_state_given
        return Foreward(self.robby)


class Start(State):
    def next_state(self):
        return Foreward(self.robby)


class End(State):
    def next_state(self):
        return None