#!/usr/bin/env python
"""\
Simple g-code streaming script for grbl
Provided as an illustration of the basic communication interface
for grbl. When grbl has finished parsing the g-code block, it will
return an 'ok' or 'error' response. When the planner buffer is full,
grbl will not send a response until the planner buffer clears space.
G02/03 arcs are special exceptions, where they inject short line
segments directly into the planner. So there may not be a response
from grbl for the duration of the arc.
---------------------
The MIT License (MIT)
Copyright (c) 2012 Sungeun K. Jeon
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
---------------------
"""

import serial
import time
import json
import datetime
import re

# Initialize previous positions
previous_x = "0.0"
previous_y = "0.0"

# Set path to position file
position_filepath = '/home/pi/Documents/Sand Table/position.json'

# Read previous position from file
with open(position_filepath) as position_file:
    position_data = json.load(position_file)
    previous_x = position_data['position']['x']
    previous_y = position_data['position']['y']
    position_file.close();

# TODO: Stop if previous_x or previous_y is empty
print('Last X: ' + previous_x)
print('Last Y: ' + previous_y)

# Open grbl serial port
grbl_serial = serial.Serial('/dev/ttyACM0',115200)

# Open g-code file
folder = '/home/pi/Documents/Sand Table/Patterns';
pattern_file = 'python-test.gcode';
gcode_file = open(folder + '/' + pattern_file,'r');

# Wake up grbl
grbl_serial.write("\r\n\r\n")

# Wait for grbl to initialize
print 'Waiting 2 seconds for GRBL to connect.'
time.sleep(2)

# Flush startup text in serial input
grbl_serial.flushInput()

# Set current position
grbl_serial.write('G10 L20 P0 X' + str(previous_x) + ' Y' + str(previous_y) + ' Z0\n');

# Stream g-code to grbl
for line in gcode_file:

    # Strip all EOL characters for consistency
    l = line.strip()

    print 'Sending: ' + l,

    # Send g-code block to grbl
    grbl_serial.write(l + '\n')

    # Wait for grbl response with carriage return
    grbl_out = grbl_serial.readline()

    print ' : ' + grbl_out.strip()

    match = re.search('WCO:(-?[0-9.]+),(-?[0-9.]+),-?[0-9.]+>$', grbl_out.strip())
    if match:
        print('Regex Group 1: ' + match.group(1))
        print('Regex Group 2: ' + match.group(2))

# TODO: Get last position, parse, and save to file
# https://pythex.org
# Sample String: <Idle|MPos:0.000,0.000,0.000|FS:0,0|WCO:-236.000,-190.000,0.000>
# grbl_serial.write('$G?\n\n')
# grbl_out = grbl_serial.readline()
# print 'Last Position: ' + grbl_out.strip()
## https://docgrbl_serial.python.org/3/library/re.html
# m = re.search('WCO:(-?[0-9.]+),(-?[0-9.]+),-?[0-9.]+>$', grbl_out.strip())
# print('Regex Group 0: ' + m.group(0))
# print('Regex Group 1: ' + m.group(1))
# Save to file
data = {
    "time": str(datetime.datetime.now()),
    "position": {
        "x": previous_x,
        "y": previous_y,
    }
}
position_file = open(position_filepath, 'w')
json.dump(data, position_file, indent=4, separators=(',', ': '))

# Wait here until grbl is finished to close serial port and file.
# raw_input("  Press <Enter> to exit and disable grbl.")

# Close file and serial port
gcode_file.close()
grbl_serial.close()
