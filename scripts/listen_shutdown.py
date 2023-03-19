#!/usr/bin/env python3

import RPi.GPIO as GPIO
import subprocess


GPIO.setmode(GPIO.BCM)
GPIO.setup(3, GPIO.IN)

# a blocking fucntion
GPIO.wait_for_edge(3, GPIO.FALLING)

#called after trigger
subprocess.call(['tvservice', '--off'], shell=False)
subprocess.call(['shutdown', '-h', 'now'], shell=False)
