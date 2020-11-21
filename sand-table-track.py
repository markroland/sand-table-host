#!/usr/bin/env python3
#
# Run a single Sand Table Pattern Track
#
#  python3 sand-table-track.py square.gcode

import argparse
import serial
import time
import json
import datetime
import re
import csv
import math
# from pathlib import Path

SERIAL_PORT = '/dev/ttyACM0'
SERIAL_BAUD_RATE = 115200
PROJECT_PATH = '/home/pi/Documents/Sand Table'

def continue_prompt():
    check = str(input("Continue ? (Y/N): ")).lower().strip()
    try:
        if check[0] == 'y':
            return True
        elif check[0] == 'n':
            return False
        else:
            print('Invalid Input')
            return continue_prompt()
    except Exception as error:
        print("Please enter valid inputs")
        print(error)
        return continue_prompt()

def config_grbl(grbl_serial):

    # Set path to config file
    config_filepath = PROJECT_PATH + '/Patterns/config.gcode'

    # Read in file
    with open(config_filepath) as fh:
        config_lines = fh.readlines()

    # Loop through command lines and send to GRBL
    for line in config_lines:
        grbl_serial.write(str.encode(line + '\n'))

def distance(A, B):
    return math.sqrt(pow(B[0] - A[0], 2) + pow(B[1] - A[1], 2))

def print_pattern(grbl_serial, pattern_file, verbose = False):

    # Initialize previous positions
    previous_x = "0.0"
    previous_y = "0.0"

    # Set path to position file
    position_filepath = PROJECT_PATH + '/' + 'position.json'

    # Read previous position from file
    with open(position_filepath) as position_file:
        position_data = json.load(position_file)
        previous_x = position_data['position']['x']
        previous_y = position_data['position']['y']
        # position_file.close()

    # TODO: Stop if previous_x or previous_y is empty
    # print('Last X: ' + previous_x)
    # print('Last Y: ' + previous_y)

    # Open g-code file
    folder = PROJECT_PATH + '/' + 'Patterns'
    gcode_file = open(folder + '/' + pattern_file,'r')

    # Flush startup text in serial input
    # grbl_serial.flushInput()

    # Set current position
    # grbl_serial.write(str.encode('G10 L20 P0 X' + str(previous_x) + ' Y' + str(previous_y) + ' Z0\n')

    # log_filepath = PROJECT_PATH + '/' + '/log.txt'

    # Stream g-code to grbl
    i = 0
    for line in gcode_file:

        i += 1

        # Strip all EOL characters for consistency
        l = line.strip()

        if verbose is True:
            print('Sending: ' + l)

        # Send g-code block to grbl
        grbl_serial.write(str.encode(l + '\n'))

        # Write progress to file
        # with open(log_filepath, 'w') as log_file:
            # log_file.write(i + ") " + '\n')
            # log_file.close()

        # Wait for grbl response with carriage return
        grbl_out = grbl_serial.readline()

        if verbose is True:
            print(' : ' + grbl_out.strip().decode('utf-8'))

        # Parse out X and Y positions from command
        # Note: This assumes X comes before Y
        match = re.search('G0\s?X(-?[0-9.]+)\s?Y(-?[0-9.]+)', l)
        if match:
            previous_x = match.group(1)
            previous_y = match.group(2)

        # Debug Work Coordinates
        # match = re.search('WCO:(-?[0-9.]+),(-?[0-9.]+),-?[0-9.]+>$', grbl_out.strip().decode('utf-8'))
        # if match:
            # previous_x = match.group(1)
            # previous_y = match.group(2)
            # print('Regex Group 1: ' + match.group(1))
            # print('Regex Group 2: ' + match.group(2))

    # Save plotter position coordinates to file

    # TODO: Get last position, parse, and save to file
    # https://pythex.org
    # Sample String: <Idle|MPos:0.000,0.000,0.000|FS:0,0|WCO:-236.000,-190.000,0.000>
    # grbl_serial.write(str.encode('$G?\n\n'))
    # grbl_out = grbl_serial.readline()
    # print 'Last Position: ' + grbl_out.strip().decode('utf-8')
    ## https://docgrbl_serial.python.org/3/library/re.html
    # m = re.search('WCO:(-?[0-9.]+),(-?[0-9.]+),-?[0-9.]+>$', grbl_out.strip().decode('utf-8'))
    # print('Regex Group 0: ' + m.group(0))
    # print('Regex Group 1: ' + m.group(1))

    data = {
        "time": str(datetime.datetime.now()),
        "position": {
            "x": previous_x,
            "y": previous_y,
        }
    }

    with open(position_filepath, 'w') as position_file:
        json.dump(data, position_file, indent=4, separators=(',', ': '))
        position_file.close()

    # Wait here until grbl is finished to close serial port and file.
    # input("  Press <Enter> to exit and disable grbl.")

    # Close file and serial port
    gcode_file.close()

# Parse input
parser = argparse.ArgumentParser()
parser.add_argument("track", type=str, help="Enter the name of the track")
parser.add_argument("-v", "--verbose", action='store_true', help="Display verbose output")
args = parser.parse_args()

# Open GRBL serial port
grbl_serial = serial.Serial(SERIAL_PORT, SERIAL_BAUD_RATE)

# Wake up grbl
grbl_serial.write(str.encode("\r\n\r\n"))

# Set path to position file
position_filepath = PROJECT_PATH + '/' + 'position.json'

# Read previous position from file
previous_x = 0.0
previous_y = 0.0
with open(position_filepath) as position_file:
    position_data = json.load(position_file)
    previous_x = float(position_data['position']['x'])
    previous_y = float(position_data['position']['y'])
    previous_time = position_data['time']
    position_file.close()

# Parse GRBL Config for plotter speed values
rate = None
with open(PROJECT_PATH + '/Patterns/config.gcode', 'r') as grbl_config:
    for line in grbl_config:
        match = re.search('\$110=([0-9\.]+)', line)
        if match is not None:
            speed_x = float(match.group(1))
        match = re.search('\$111=([0-9\.]+)', line)
        if match is not None:
            speed_y = float(match.group(1))
rate = min(speed_x, speed_y)

# Parse pattern file
steps = 0
total_distance = 0
estimated_time = None
with open(PROJECT_PATH + '/' + 'Patterns' + '/' + args.track, 'r') as track_gcode:

    x_last = previous_x
    y_last = previous_y
    for line in track_gcode:

        # Parse out X and Y positions from command
        # Note: This assumes X comes before Y
        match = re.search('G0\s?X(-?[0-9.]+)\s?Y(-?[0-9.]+)', line)
        if match:
            steps = steps + 1
            x = float(match.group(1))
            y = float(match.group(2))

            total_distance = total_distance + distance((x_last, y_last), (x,y))

            x_last = x
            y_last = y

    if rate is not None:
        estimated_time = total_distance / (rate/60)

    track_gcode.close()

# Check last recorded position.
# User should not proceed if the coordinates don't appear to accurately
# represent the device
print('Track: ' + args.track)
print('Steps: ' + "{:,d}".format(steps))
print('Distance: ' + str(round(total_distance/1000, 2)) + ' meters')
print('Estimated Time: ' + str(round(estimated_time, 2)) + ' seconds')
print('--------------------------')
print('Last Position Recorded: ' + previous_time)
print('Current X Position: ' + str(previous_x))
print('Current Y Position: ' + str(previous_y))
print('--------------------------')

# Get confirmation to continue
if continue_prompt() is not True:
    print('Cancelled')
    grbl_serial.close()
    quit()

# TODO: Estimate finish Time

# Wait for grbl to initialize
print('Connecting to GRBL...')
time.sleep(2)
print('Connected.')

# Flush startup text in serial input
grbl_serial.flushInput()

# Set current position
grbl_serial.write(str.encode('G10 L20 P0 X' + str(previous_x) + ' Y' + str(previous_y) + ' Z0\n'))

# Display current pattern printing
print('Printing ' + args.track + '...')

# Send GRBL configuration (speed, acceleration, etc.)
config_grbl(grbl_serial)

# Print file contents
print_pattern(grbl_serial, args.track, args.verbose)

# TODO: Leave open until estimated finish time?

# Close GRBL serial
grbl_serial.close()

# Print closing statement
print('--------------------------')
print('Completed at ' + datetime.datetime.now())
