# Sand Table Server
#
# Run as root
#
# Run in background:
#  nohup sudo python index.py > /dev/null 2>&1 &
#
# curl http://192.168.0.14:5007/job
# curl -X PUT -d "value=1" http://192.168.0.14:5007/job
#

import serial
import time

from flask import Flask, request, render_template

## Logging
#logger = logging.getLogger('werkzeug')
#handler = logging.FileHandler('access.log')
#logger.addHandler(handler)
#
# Also add the handler to Flask's logger for cases
#  where Werkzeug isn't used as the underlying WSGI server.
#app.logger.addHandler(handler)
## End Logging


# Create new Flask app
app = Flask(__name__)

# Define route: Default
# @app.route('/')
# def index():
#     return render_template('index.html')

# Define route: Pin
@app.route('/job', methods=['Get','POST'])
def job():
    if request.method == 'GET':

        # Open grbl serial port
        s = serial.Serial('/dev/ttyACM0',115200)

        # Open g-code file
        folder = '/home/pi/Documents/Sand Table/Patterns';
        file = 'python-test.gcode';
        f = open(folder + '/' + file,'r');

        # Wake up grbl
        s.write("\r\n\r\n")
        time.sleep(2)   # Wait for grbl to initialize
        s.flushInput()  # Flush startup text in serial input

        # Stream g-code to grbl
        for line in f:
            l = line.strip() # Strip all EOL characters for consistency
            # print 'Sending: ' + l,
            s.write(l + '\n') # Send g-code block to grbl
            grbl_out = s.readline() # Wait for grbl response with carriage return
            # print ' : ' + grbl_out.strip()

        # Close file and serial port
        f.close()
        s.close()

        response = 'GET'
    if request.method == 'POST':
        response = 'POST'
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5007)
