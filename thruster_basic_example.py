###############################################################
# This is a library for the SeaDroneTM Smart Thruster Driver.
# It allows to control up to 15 brushless motors from a single
# serial port and provide real time feedback for the velocity,
# current, voltage and temperature of each driver.
#
# Designed specifically to work with the
# SeaDroneTM Smart Thruster Breakout Board:
# https://seadronepro.com/shop-seadrone/
#
# These motor drivers use the serial port to communicate,
# so a total of 2 pins (TX and RX) are required as interface.
# The open source breakout board is also compatible with most
# USB-to-serial 3.3V adapters, to be plugged into any USB port.
#
# Author:   Carlos Garcia-Saura (@CarlosGS)
# Copyright (C) 2017 SeaDroneTM (www.seadronepro.com)
# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public
# License v3 as published by the Free Software Foundation.
###############################################################

import seadrone.smart_thruster as thrusters
import time

N_motors = 4
port = '/dev/ttyUSB0'

print("Starting motors...")
m = thrusters.start(N_motors, port)

print("Setting velocities...")
m.target_rpm[1] = 300 # set the speed of motor #1 to 300RPM
m.target_rpm[2] = 400 # set the speed of motor #2 to 400RPM
m.target_rpm[3] = 500 # set the speed of motor #3 to 500RPM
m.target_rpm[4] = -600 # this motor will spin counter-clockwise

try:
    while True:
        print("\n\n\n\n") # empty lines for space
        for id in m.motors:
            rpm = m.rpm[id] # read the feedback of each motor
            amps = m.current[id]
            volts = m.voltage[id]
            temp = m.driver_temperature[id]
            alarm = m.get_alarm_description(id)
            print("Motor %d: %dRPM %.3fA %.3fV %.1fC Alarm: %s" % (id,rpm,amps,volts,temp,alarm))
            if m.has_alarm[id]:
                m.reset_alarm(id) # Auto-reset motor alarm
        time.sleep(0.1) # wait 100ms after each printout
except KeyboardInterrupt:
    print("Shutting down smart thruster library...")

m.stop()




