#!/usr/bin/env python3
#
# Run a Playlist of multilple Tracks
#
#  python3 sand-table-player.py playlist-1

import argparse
import serial
import time
import json
import datetime
import re
import csv

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

def print_pattern(grbl_serial, pattern_file, verbose = False):

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
        # position_file.close()

    # TODO: Stop if previous_x or previous_y is empty
    # print('Last X: ' + previous_x)
    # print('Last Y: ' + previous_y)

    # Open g-code file
    folder = '/home/pi/Documents/Sand Table/Patterns'
    gcode_file = open(folder + '/' + pattern_file,'r')

    # Flush startup text in serial input
    # grbl_serial.flushInput()

    # Set current position
    # grbl_serial.write(str.encode('G10 L20 P0 X' + str(previous_x) + ' Y' + str(previous_y) + ' Z0\n'))

    # Stream g-code to grbl
    for line in gcode_file:

        # Strip all EOL characters for consistency
        l = line.strip()

        if verbose is True:
            print('Sending: ' + l)

        # Send g-code block to grbl
        grbl_serial.write(str.encode(l + '\n'))

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

        match = re.search('WCO:(-?[0-9.]+),(-?[0-9.]+),-?[0-9.]+>$', grbl_out.strip().decode('utf-8'))
        if match:
            # previous_x = match.group(1)
            # previous_y = match.group(2)
            print('Regex Group 1: ' + match.group(1))
            print('Regex Group 2: ' + match.group(2))

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
    # Save to file
    #
    data = {
        "time": str(datetime.datetime.now()),
        "position": {
            "x": previous_x,
            "y": previous_y,
        }
    }
    print(data)
    with open(position_filepath, 'w') as position_file:
        json.dump(data, position_file, indent=4, separators=(',', ': '))
        # position_file.close()

    # Wait here until grbl is finished to close serial port and file.
    # raw_input("  Press <Enter> to exit and disable grbl.")

    # Close file and serial port
    gcode_file.close()

# Parse input
parser = argparse.ArgumentParser()
parser.add_argument("playlist", type=str, help="Enter the name of the playlist, excluding the .csv extension")
parser.add_argument("-d", "--delay", type=float, default=0.0, help="A delay, in seconds, between playing each track")
parser.add_argument("-v", "--verbose", action='store_true', help="Display verbose output")
args = parser.parse_args()

# Define playlist file to read
playlist_filepath = "/home/pi/Documents/Sand Table/playlists/" + args.playlist + ".csv"
print('Playing:  ' + playlist_filepath)

# Open GRBL serial port
grbl_serial = serial.Serial('/dev/ttyACM0', 115200)

# Wake up grbl
grbl_serial.write(str.encode("\r\n\r\n"))

# Set path to position file
position_filepath = '/home/pi/Documents/Sand Table/position.json'

# Read previous position from file
with open(position_filepath) as position_file:
    position_data = json.load(position_file)
    previous_x = position_data['position']['x']
    previous_y = position_data['position']['y']
    previous_time = position_data['time']
    position_file.close()

# Check last recorded position.
# User should not proceed if the coordinates don't appear to accurately
# represent the device
print('Last Position Recorded: ' + previous_time)
print('Current X Position: ' + previous_x)
print('Current Y Position: ' + previous_y)

# Get confirmation to continue
if continue_prompt() is not True:
    print('Cancelled')
    grbl_serial.close()
    quit()

# Wait for grbl to initialize
print('Waiting 2 seconds for GRBL to connect.')
time.sleep(2)

# Flush startup text in serial input
grbl_serial.flushInput()

# Set current position
grbl_serial.write(str.encode('G10 L20 P0 X' + str(previous_x) + ' Y' + str(previous_y) + ' Z0\n'))

# Read playlist from file
try:
    with open(playlist_filepath) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:

            # Display current pattern printing
            print('Printing ' + row['Filename'])

            # Print file contents
            print_pattern(grbl_serial, row['Filename'], args.verbose)

            # Delay before starting next track
            time.sleep(args.delay)

except IOError as e:
    print "Unable to open file"

# Close GRBL serial
grbl_serial.close()

print('Complete')
