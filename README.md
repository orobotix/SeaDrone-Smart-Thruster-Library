
# SeaDrone Smart Thruster Library

This Python library allows to control up to 15 brushless motors from a single serial port and provide real time feedback for the velocity, current, voltage and temperature of each driver.

Designed specifically to work with the SeaDroneTM Smart Thruster Breakout Board: <https://seadronepro.com/shop-seadrone/>

**These motor drivers use the serial port to communicate, so a total of 2 pins (TX and RX) are required as interface. The open source breakout board is also compatible with most USB-to-serial 3.3V adapters, to be plugged into a USB port.**


Usage guide
===========
The SeaDrone Python library is generic and should run in any environment that supports Python 3.

Setup for Debian-based Linux (Ubuntu, Raspbian, etc)
- In a terminal, run ``sudo apt update`` and ``sudo apt upgrade``
- Make sure the dependencies are installed: ``sudo apt install python3 python3-serial``

To run the examples:
- Download a copy of this repository.
- Connect the Smart Thrusters to a serial port in the computer.
- Find the ID of the serial port (you can use the command ``ls /dev``). If needed, update the variable ``port = '/dev/ttyUSB0'`` in each example code.
- To run the basic example: ``python3 thruster_advanced_example.py`` (you can stop any script using CTRL+C).
- To run the advanced example: ``python3 thruster_advanced_example.py``
- That's it! Empower your underwater robots with the Seadrone Smart Thrusters!

Any questions? We are here to help! [Report a new issue](../../issues)


Safety notes
============
- **High power motors can be dangerous. The propellers can act as sharp blades at high speeds. Make sure to firmly clamp down the thrusters and wear safety equipment (goggles, gloves, etc), specially during initial tests.**
- **Always disconnect all power sources before rewiring a circuit. Otherwise the electronics could be damaged.**
- **For example, if you need to swap a motor or a driver, make sure to unpower everything first.**

**SeaDrone is not liable for any damage derived from the misuse of the SeaDrone Smart Thrusters electronics, hardware and/or software.**


License
=======

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

_Author: Carlos Garcia-Saura (@CarlosGS). Copyright (C) 2017 SeaDroneTM (www.seadronepro.com)_

