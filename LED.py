import RPi.GPIO as GPIO #pip3 install RPi.GPIO
import time


blue=11
red=15
green=13
def LED_setup():
	listLight=[red, green, blue]
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(listLight,GPIO.OUT)

def red_LED():
	GPIO.output(green, False)
	GPIO.output(blue, False)
	GPIO.output(red, True)
	time.sleep(5)

def green_LED():
	GPIO.output(green, True)
	GPIO.output(blue, False)
	GPIO.output(red, False)
	time.sleep(5)

def blue_LED():
	GPIO.output(green, False)
	GPIO.output(red,   False)
	GPIO.output(blue,  True)
	time.sleep(5)

def all_LED():
	GPIO.output(green, True)
	GPIO.output(red, True)
	GPIO.output(blue, True)
	time.sleep(5)

LED_setup()
all_LED()
red_LED()
green_LED()
blue_LED()
