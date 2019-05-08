# This file will run the fingerprint reader and communicate with the server via
# python requests library
import requests
from pygame import mixer
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
	GPIO.output(blue,  False)
	GPIO.output(red,   True)
	time.sleep(5)

def green_LED():
	GPIO.output(green, True)
	GPIO.output(blue,  False)
	GPIO.output(red,   False)
	time.sleep(5)

def blue_LED():
	GPIO.output(green, False)
	GPIO.output(red,   False)
	GPIO.output(blue,  True)
	time.sleep(5)

def all_on_LED():
	GPIO.output(green, True)
	GPIO.output(red,   True)
	GPIO.output(blue,  True)
	time.sleep(5)
def all_off_LED():
	GPIO.output(blue,   False)
	GPIO.output(red,    False)
	GPIO.output(green,  False)


LED_setup()

def beep():
	mixer.init()
	alert = mixer.Sound('beep.wav')
	alert.play()
	time.sleep(2)
	mixer.quit()
