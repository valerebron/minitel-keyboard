import RPi.GPIO as GPIO
import time
import re
from evdev import UInput, InputDevice, ecodes as e
import os

# list of all involved pins (Every GPIO pins, and all special features disabled)
ALLS = [ 27, 3, 4, 7, 8, 9, 10, 11, 14, 15, 23, 17, 18, 22, 24, 25 ]
# Pins used to send current
OUTS = [ 3 , 4, 7, 8, 17, 18, 22, 24 ]
# Pins used to detect current
INS=list(set(ALLS) - set(OUTS))

keymap = dict()
for i in ALLS:
	keymap[i] = dict()
	for u in ALLS:
		keymap[i][u] = ""

def save():
	keyfile = open("keymap.conf", "w")
	for i in OUTS:
	        for u in INS:
        	        keyfile.write(str(i)+":"+str(u)+"="+keymap[i][u]+"\n")

GPIO.setmode(GPIO.BCM)
ui =  UInput()
try:
	keyfile = open("keymap.conf", "r")
	exp = re.compile("([0-9]+):([0-9]+)=(.+)")
	for match in exp.finditer(keyfile.read()):
		keymap[int(match.group(1))][int(match.group(2))]=match.group(3)
except:
	print("No keymap detected.")


for chan in OUTS:
	GPIO.setup(chan, GPIO.OUT, initial=0)

for chan in INS:
	GPIO.setup(chan, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

try:
	while True:
		for out in OUTS:
			GPIO.output(out, 1)
			for chan in INS:
				if GPIO.input(chan) == 1:
					if keymap[out][chan] != "":
						ui.write(e.EV_KEY, e.ecodes[keymap[out][chan]], 1)
						ui.write(e.EV_KEY, e.ecodes[keymap[out][chan]], 0)
						ui.syn()
						time.sleep(0.05)
					else:
						keymap[out][chan] = input("Unknown keycode, which key did you press ?\n")
						save()
			GPIO.output(out, 0)
			time.sleep(0.01)
finally:
	GPIO.cleanup()
	ui.close()
