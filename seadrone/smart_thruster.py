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

# Begin modules
import sys
import time
import serial
import threading
import struct
# End modules

if sys.version_info < (3, 0):
    print("This script requires python version >3.0")
    exit()


class start():
    def __init__(self, N_motors, port):
        self.running = True
        self.motors = [i+1 for i in range(N_motors)]
        self.is_on = [False for i in range(N_motors+1)]
        self.target_rpm = [0 for i in range(N_motors+1)]
        self.rpm = [0 for i in range(N_motors+1)]
        self.current = [0. for i in range(N_motors+1)]
        self.voltage = [0. for i in range(N_motors+1)]
        self.driver_temperature = [0. for i in range(N_motors+1)]
        self.has_alarm = [0 for i in range(N_motors+1)]
        self.alarm_code = [0 for i in range(N_motors+1)]
        
        self.keep_enabled = [False for i in range(N_motors+1)]
        
        self.request_alarm_reset = [False for i in range(N_motors+1)]
        
        self.alarm_description = {}
        self.alarm_description[0] = "No alarm"
        self.alarm_description[16] = "Driver temperature too high"
        self.alarm_description[18] = "Input voltage too high"
        self.alarm_description[19] = "Input voltage too low"
        self.alarm_description[20] = "Motor speed/acceleration too high"
        self.alarm_description[21] = "Over current, payload is too high"
        self.alarm_description[26] = "Alarm 0x1A, overcurrent"
        
        self.serial = serial.Serial(
            port=port,
            baudrate=921600,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_TWO,
            timeout=0.001 # needs to be long enough to ensure driver response is fully captured
        )
        
        if not self.serial.isOpen(): raise Exception("ERROR: Failed to open the serial port "+serialDevice)
        
        for id in self.motors:
            self.motor_set_rpm(id, 0)
            self.motor_reset_alarm(id)
        
        def motorx_thread(self):
            while self.running:
                for id in self.motors:
                    if self.request_alarm_reset[id]:
                        self.motor_reset_alarm(id)
                        self.request_alarm_reset[id] = False
                    self.motor_set_rpm(id, self.target_rpm[id])
                    self.read(id)
                time.sleep(0.01) # some rest for the CPU
            for id in self.motors: # shut down the motors
                self.motor_set_rpm(id, 0)
                self.motor_enable(id, False)
        
        self.thread = threading.Thread(target=motorx_thread, args=(self,))
        self.thread.daemon = True
        self.thread.start()
    
    def reset_alarm(self, id):
        if self.request_alarm_reset[id] != True:
            self.request_alarm_reset[id] = True
    
    def get_alarm_description(self, id):
        alarm_code = self.alarm_code[id]
        if alarm_code in self.alarm_description:
            return self.alarm_description[alarm_code]
        return "Unkown alarm code %d" % alarm_code
    
    def read(self, id):
        driver_read = self.serial_packet(id, self.cmd_read(1700)+self.cmd_read(1107)+self.cmd_read(1116)+self.cmd_read(1123)+self.cmd_read(1124), reply=True)
        self.serial.flush()
        self.serial.write(driver_read)
        raw_packet = self.serial.read(100) # TODO calculate max possible packet length
        if len(raw_packet) > 0:
            packet = list(raw_packet)
            self.parse_packet(packet)
    
    def send(self, packet):
        self.serial.write(packet)
    
    def motor_reset_alarm(self, id):
        driver_reset_alarm = self.serial_packet(id, self.cmd_write(2032, 1))
        self.send(driver_reset_alarm)
    
    def motor_enable(self, id, enable):
        driver_start = self.serial_packet(id, self.cmd_write(2000, int(enable)))
        self.send(driver_start)

    def motor_set_rpm(self, id, target_rpm):
        direction = (1 if target_rpm > 0 else -1)
        rpm = abs(target_rpm)
        if rpm > 5500: rpm = 5500
        if rpm < 300: rpm = 0
        enable = 1
        if rpm == 0 and self.keep_enabled[id] == False: enable = 0
        driver_set_speed = self.serial_packet(id, self.cmd_write(2001, direction)+self.cmd_write(2002, rpm)+self.cmd_write(2000, enable))
        self.send(driver_set_speed)
    
    def serial_packet(self, id, data=[], reply=False):
        packet = [id,int(len(data)/2) | ((not reply) << 7)] + data
        return packet + self.checksum(packet)

    def checksum(self, packet):
        lsb = 0
        msb = 0
        for i in range(int(len(packet)/2)): # Add XOR CRC
            lsb ^= packet[i*2]   # LSB
            msb ^= packet[i*2+1] # MSB
        return [lsb, msb]

    def cmd_parse(self, cmd_raw):
        bits32 = cmd_raw[1] >> 7
        if (len(cmd_raw) < 6 and bits32) or (len(cmd_raw) < 4 and not bits32):
            print("WARNING: Bad raw command size! Discarding...")
            return(-1, -1, -1)
        WR = (cmd_raw[1] >> 6) & 0x1
        index = cmd_raw[0] | ((cmd_raw[1] & 0xF) << 8)
        value = 0
        if bits32:
            value = struct.unpack("i", bytearray(cmd_raw[2:6]))[0]
            nextStartByte = 6
        else:
            print("Warning: Received 16 bit value!")
            value = struct.unpack("h", bytearray(cmd_raw[2:4]))[0]
            nextStartByte = 4
        moreCommands = cmd_raw[nextStartByte:]
        return (index, value, moreCommands)

    def cmd_generic(self, WR, index, value):
        index_msb = (index >> 8) & 0xF
        index_lsb = index & 0xFF
        bits32 = 1
        return [index_lsb, index_msb | (bits32 << 7) | (WR << 6), value & 0xFF, (value >> 8) & 0xFF, (value >> 16) & 0xFF, (value >> 24) & 0xFF]

    def cmd_read(self, index):
        return self.cmd_generic(0, index, 0)

    def cmd_write(self, index, value):
        return self.cmd_generic(1, index, value)

    def parse_packet(self, packet):
        crc = self.checksum(packet[:-2])
        if crc != packet[-2:]:
            print("ERROR: Bad checksum for inbound packet! Discarding...")
            return (-1,-1,[])
        driver_id = packet[0]
        servo_alarm = packet[1] >> 7
        servo_on = (packet[1] & 0x40) >> 6
        packet_size = packet[1] & 0x1F
        
        measured_size = len(packet)/2 - 2
        if measured_size != packet_size:
            print("ERROR: Bad size argument for inbound packet! Discarding...")
            return (-1,-1,[])

        data = packet[2:-2]
        
        self.is_on[driver_id] = servo_on
        self.has_alarm[driver_id] = servo_alarm
        
        moreCommands = data
        while len(moreCommands) > 0:
            (index, value, moreCommands) = self.cmd_parse(moreCommands)
            if index == 1700: self.alarm_code[driver_id] = value
            if index == 1107: self.rpm[driver_id] = value
            if index == 1116: self.current[driver_id] = value/100.
            if index == 1124: self.voltage[driver_id] = value/10.
            if index == 1123: self.driver_temperature[driver_id] = value/10.
        
        return (driver_id, servo_alarm, servo_on, data)

    def stop(self):
        self.running = False
        self.thread.join()

