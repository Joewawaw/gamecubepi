#!/usr/bin/env python3

from flask import Flask, request, redirect
import sys, time

app = Flask(__name__)


@app.route('/submit', methods=['POST'])
def submit():
    wifi_name = request.form['wifi_name']
    password = request.form['password']

    wpa_supplicant_config = f'''
network={{
        ssid="{wifi_name}"
        scan_ssid=1
        psk="{password}"
        proto=RSN
        key_mgmt=WPA-PSK
}}
'''

    # Open the wpa_supplicant configuration file in write mode
    with open('/etc/wpa_supplicant/wpa_supplicant.conf', 'a') as f:
        # Write the wpa_supplicant configuration to the file
        f.write(wpa_supplicant_config)

    with open('/home/keshav/wifi-is-set', 'w') as f:
        f.write('1')
    time.sleep(3)
    with open('/home/keshav/wifi-is-set', 'w') as f:
        f.write('0')

    return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Success</title>
        </head>
        <body>
            <h1>Success!</h1>
            <p>Your WiFi credentials have been saved. You can now connect to the internet.</p>
        </body>
        </html>
    '''

if __name__ == '__main__':
    app.run()
