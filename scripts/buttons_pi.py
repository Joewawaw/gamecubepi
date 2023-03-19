#!/usr/bin/env python3

import RPi.GPIO as GPIO
import logging
from time import sleep
import subprocess

LOG_LEVEL=logging.DEBUG
###############################################################################
def main():
  GPIO.setmode(GPIO.BCM)     # set up BCM GPIO numbering
  logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%I:%M:%S %p',level=LOG_LEVEL)

  #pin numbers: https://www.raspberrypi-spy.co.uk/wp-content/uploads/2012/06/Raspberry-Pi-GPIO-Header-with-Photo.png
  open_pin=4
  power_pin=3
  reset_pin=2

  #timeout in ms
  OPEN_HELD_TIMEOUT=2000
  POWER_HELD_TIMEOUT=2000
  RESET_HELD_TIMEOUT=2500

  #set up inputs with internal pull up resistor (pins 2 & 3 have a hard pull-up, so no need to enable the soft one)
  GPIO.setup(power_pin,  GPIO.IN)
  GPIO.setup(open_pin, GPIO.IN,GPIO.PUD_UP)
  GPIO.setup(reset_pin, GPIO.IN)

  # We always disable the wlan0 wifi on startup, easiest way is to do it here
  sleep(10)
  subprocess.run(['sudo', 'ifconfig', 'wlan0', 'down'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=False)
  sleep(3)

  logging.debug('Start')

  mycounter=0
  try:
    while True:
      mycounter = (mycounter+1) % 15
      gpio_handler(power_pin, POWER_HELD_TIMEOUT, "POWER")
      gpio_handler(reset_pin, RESET_HELD_TIMEOUT, "RESET")
      gpio_handler(open_pin,  OPEN_HELD_TIMEOUT,  "OPEN")

      if mycounter == 0:
        subprocess.run(['sudo', '/home/keshav/window_focus.sh'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=False)

      sleep(0.1)
  finally:
    GPIO.cleanup()

##################################################################################3
def gpio_handler(pin, timeout_ms, name="GPIO"):
  # this is the trigger to this function, if unpressed (HIGH) then it will pass
  if not GPIO.input(pin):
    sleep(0.05) #debounce before

    timer = 0
    while timer < (timeout_ms/10):
      timer+=1
      if GPIO.input(pin):
        timer=-1
        break
      sleep(0.010)
    if timer == -1:
      logging.debug(name+" Button Press\n")
      press_callback(name)
    else:
      logging.debug(name+" Button Hold\n")
      held_callback(name)
      while not GPIO.input(pin): pass

    sleep(0.05) # debounce after

def held_callback(name):
  if name == 'POWER':
    # Shutdown & Turn off TV
    subprocess.run(['/home/keshav/tv_cec_off.sh'],       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=False)
    subprocess.Popen(['sudo', 'shutdown', '-h', 'now'],   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=False)
  elif name == 'RESET':
    # Enable Wi-Fi AP (Captive Portal)
    subprocess.Popen(['sudo', 'ifconfig', 'wlan0', 'up'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=False)
    sleep(10)
    wifi_flask = subprocess.Popen(['sudo', 'python3', '/home/keshav/wifi_portal.py'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=False)
    subprocess.run(['sudo', 'nginx'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=False)
    sleep(5)
    #wifi config is complete when this file is 1
    while 1:
      with open('/home/keshav/wifi-is-set', 'r') as f:
        if f.read() == '1':
          break
      sleep(1)

    sleep(5)
    subprocess.Popen(['sudo', 'nginx', '-s', 'stop'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=False)
    wifi_flask.kill()
    subprocess.Popen(['sudo', 'ifconfig', 'wlan0', 'down'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=False)
    subprocess.Popen(['sudo', 'systemctl', 'restart', 'wpa_supplicant'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=False)
    subprocess.Popen(['wpa_cli', '-i', 'wlan1', 'reconfigure'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=False)
  elif name == 'OPEN':
    # Enable Bluetooth pairing
    pass

def press_callback(name):
  if name == 'POWER':
    # Shutdown (turn off screen before)
    subprocess.run(['tvservice', '--off'], shell=False)
    subprocess.Popen(['sudo', 'shutdown', '-h', 'now'], shell=False)
  elif name == 'RESET':
    # Quit & Leave Session
    subprocess.run(['xdotool', 'key', 'Ctrl+Alt+Shift+Q'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=False)
    subprocess.run(['moonlight-qt', 'quit', 'keshavnet'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=False)
    sleep(7)
    subprocess.run(['xdotool', 'key', 'Escape'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=False)
  elif name == 'OPEN':
    # Rumble Test (all 4 controllers)
    subprocess.Popen(['/home/keshav/rumble-test/rumble-test', '/dev/input/event0', '1'], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL, shell=False)
    subprocess.Popen(['/home/keshav/rumble-test/rumble-test', '/dev/input/event1', '1'], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL, shell=False)
    subprocess.Popen(['/home/keshav/rumble-test/rumble-test', '/dev/input/event2', '1'], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL, shell=False)
    subprocess.Popen(['/home/keshav/rumble-test/rumble-test', '/dev/input/event3', '1'], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL, shell=False)
###############################################################################3
if __name__=="__main__":
  main()
