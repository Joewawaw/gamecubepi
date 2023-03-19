#!/usr/bin/env bash
if ! xdotool getwindowfocus; then xdotool search --class moonlight > xdotool windowfocus; xdotool mousemove 1919 1079; fi
