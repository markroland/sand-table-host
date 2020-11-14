#!/usr/bin/env python

import serial
import time
import re

# Open grbl serial port
grbl_serial = serial.Serial('/dev/ttyACM0',115200)

# Wake up grbl
grbl_serial.write("\r\n\r\n")

# Wait for grbl to initialize
print 'Waiting 2 seconds for GRBL to connect.'
time.sleep(2)

# Flush startup text in serial input
grbl_serial.flushInput()

def prompt():
    jog_x = input("Jog X: ");
    jog_y = input("Jog Y: ");
    return (jog_x, jog_y)

# Prompt for X,Y values
values = prompt()

# Repeat until (0,0) values are entered meaning do not move X or Y
while values[0] != 0 or values[1] != 0:

    # Build Jog Command (https://github.com/gnea/grbl/wiki/Grbl-v1.1-Jogging)
    grbl_command = "$J=G21G91X" + str(values[0]) + "Y" + str(values[1]) + "F8000"

    # Send g-code block to grbl
    # print(grbl_command)
    grbl_serial.write(grbl_command + '\n')

    # Repeat Prompt
    values = prompt()

# Close file and serial port
grbl_serial.close()
