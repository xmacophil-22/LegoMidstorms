#!/usr/bin/env python3
from my_Robot import *
from states import *

if __name__ == "__main__":
    robby = Robot()
    robby.TANK.on(SpeedPercent(robby.CURRENT_SPEED), SpeedPercent(robby.CURRENT_SPEED))
    # calibrate_ultra(robby)
    # calibrate_sensors(robby)
    current_state = Start(robby)
    while current_state is not None:
        # current_state.be_vocal()
        current_state = current_state.next_state()