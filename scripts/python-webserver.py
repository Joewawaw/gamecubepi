#!/usr/bin/env python3

import RPi.GPIO as GPIO
import os
import time
import subprocess
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer

#host_name = '10.0.0.184'  # IP Address of Raspberry Pi
host_port = 8000


def setupGPIO():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    GPIO.setup(14, GPIO.OUT)

class MyServer(BaseHTTPRequestHandler):

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def _redirect(self, path):
        self.send_response(303)
        self.send_header('Content-type', 'text/html')
        self.send_header('Location', path)
        self.end_headers()

    def do_GET(self):
        html = '''
           <html>
           <body 
            style="width:960px; margin: 20px auto;">
           <h1>Keshavnet's Watering System!</h1>
           <form action="/" method="POST">
               Water Pump
               <input type="submit" name="submit" value="ON">
               <input type="submit" name="submit" value="OFF">
               <br>
               <br>
               <label for="time"> Enter time in seconds (3-60)    </label>
               <input type="number" id="time" name="time" value="5" min="5" max="60">

               <br>
               <label for="mL"> OR </label>
               <br>
               <label for="mL"> Enter volume in milliliters (25-250)     </label>
               <input type="number" id="mL" name="mL" value="0" min="0" max="250">
           </form>
           </body>
           </html>
        '''
        self.do_HEAD()
        self.wfile.write(html.format('0').encode("utf-8"))

    def do_POST(self):
        import os
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode("utf-8")
        ml_data = post_data.split('&')[2].split('=')[1]
        time_data = post_data.split('&')[1].split('=')[1]
        gpio_data = post_data.split('&')[0].split("=")[1]

        setupGPIO()

        if ml_data != '0':
            #integer division by 17
            time_data = str((int(ml_data)+1)//17)

        if gpio_data == 'ON':
            subprocess.Popen(['python', '/home/keshav/gpio_toggle.py', time_data])
            print('Pump is {} for {}s'.format(gpio_data, time_data))

        elif gpio_data == 'OFF':
            GPIO.output(14, GPIO.LOW)
            print('Pump is OFF')

        self._redirect('/')  # Redirect back to the root url

# # # # # Main # # # # #
if __name__ == '__main__':
    http_server = HTTPServer(('192.168.10.192', host_port), MyServer)
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
    logging.info('server start')
    os.environ['PUMP_SET'] = '0'
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        http_server.server_close()
