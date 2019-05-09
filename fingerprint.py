import json
import time
import adafruit_fingerprint
import pymongo
import datetime
import requests
from requests import auth
from pygame import mixer
import RPi.GPIO as GPIO #pip3 install RPi.GPIO
import sys
#adding-from-client--------------------------------------------------------------------------
IP_Address = str(sys.argv[1])
blue=11
red=15
green=13

listLight=[red, green, blue]
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(listLight,GPIO.OUT)

def red_LED():
    GPIO.output(green, False)
    GPIO.output(blue,  False)
    GPIO.output(red,   True)

def green_LED():
    GPIO.output(green, True)
    GPIO.output(blue,  False)
    GPIO.output(red,   False)
    time.sleep(3)

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
    
def yellow_LED():
    GPIO.output(green, True)
    GPIO.output(red,   True)
    GPIO.output(blue,  False)
    time.sleep(2)

def all_off_LED():
    GPIO.output(blue,   False)
    GPIO.output(red,    False)
    GPIO.output(green,  False)



def beep():
    mixer.init()
    alert = mixer.Sound('beep.wav')
    alert.play()
    time.sleep(5)
    mixer.quit()


#------------------------------------------------------------------
#uart = busio.UART(board.TX, board.RX, baudrate=57600)

# If using with a computer such as Linux/RaspberryPi, Mac, Windows...
import serial
uart = serial.Serial(port="/dev/ttyS0", baudrate=57600, timeout=1)

finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)

##################################################


def get_fingerprint():
    """Get a finger print image, template it, and see if it matches!"""
    print("Waiting for image...")
    while finger.get_image() != adafruit_fingerprint.OK:
        pass
    print("Templating...")
    if finger.image_2_tz(1) != adafruit_fingerprint.OK:
        return False
    print("Searching...")
    if finger.finger_fast_search() != adafruit_fingerprint.OK:
        return False
    return True

# pylint: disable=too-many-branches
def get_fingerprint_detail():
    """Get a finger print image, template it, and see if it matches!
    This time, print out each error instead of just returning on failure"""
    print("Getting image...", end="", flush=True)
    i = finger.get_image()
    if i == adafruit_fingerprint.OK:
        print("Image taken")
    else:
        if i == adafruit_fingerprint.NOFINGER:
            print("No finger detected")
        elif i == adafruit_fingerprint.IMAGEFAIL:
            print("Imaging error")
        else:
            print("Other error")
        return False

    print("Templating...", end="", flush=True)
    i = finger.image_2_tz(1)
    if i == adafruit_fingerprint.OK:
        print("Templated")
    else:
        if i == adafruit_fingerprint.IMAGEMESS:
            print("Image too messy")
        elif i == adafruit_fingerprint.FEATUREFAIL:
            print("Could not identify features")
        elif i == adafruit_fingerprint.INVALIDIMAGE:
            print("Image invalid")
        else:
            print("Other error")
        return False

    print("Searching...", end="", flush=True)
    i = finger.finger_fast_search()
    # pylint: disable=no-else-return
    # This block needs to be refactored when it can be tested.
    if i == adafruit_fingerprint.OK:
        print("Found fingerprint!")
        return True
    else:
        if i == adafruit_fingerprint.NOTFOUND:
            print("No match found")
        else:
            print("Other error")
        return False

# pylint: disable=too-many-statements
def enroll_finger(location):
    """Take a 2 finger images and template it, then store in 'location'"""
    for fingerimg in range(1, 3):
        if fingerimg == 1:
            print("Place finger on sensor...", end="", flush=True)
        else:
            print("Place same finger again...", end="", flush=True)

        while True:
            i = finger.get_image()
            if i == adafruit_fingerprint.OK:
                print("Image taken")
                break
            elif i == adafruit_fingerprint.NOFINGER:
                print(".", end="", flush=True)
            elif i == adafruit_fingerprint.IMAGEFAIL:
                print("Imaging error")
                return False
            else:
                print("Other error")
                return False

        print("Templating...", end="", flush=True)
        i = finger.image_2_tz(fingerimg)
        if i == adafruit_fingerprint.OK:
            print("Templated")
        else:
            if i == adafruit_fingerprint.IMAGEMESS:
                print("Image too messy")
            elif i == adafruit_fingerprint.FEATUREFAIL:
                print("Could not identify features")
            elif i == adafruit_fingerprint.INVALIDIMAGE:
                print("Image invalid")
            else:
                print("Other error")
            return False

        if fingerimg == 1:
            print("Remove finger")
            time.sleep(1)
            while i != adafruit_fingerprint.NOFINGER:
                i = finger.get_image()

    print("Creating model...", end="", flush=True)
    i = finger.create_model()
    if i == adafruit_fingerprint.OK:
        print("Created")
    else:
        if i == adafruit_fingerprint.ENROLLMISMATCH:
            print("Prints did not match")
        else:
            print("Other error")
        return False

    print("Storing model #%d..." % location, end="", flush=True)
    i = finger.store_model(location)
    if i == adafruit_fingerprint.OK:
        print("Stored")
    else:
        if i == adafruit_fingerprint.BADLOCATION:
            print("Bad storage location")
        elif i == adafruit_fingerprint.FLASHERR:
            print("Flash storage error")
        else:
            print("Other error")
        return False

    return True


##################################################

def get_num():
    """Use input() to get a valid number from 1 to 127. Retry till success!"""
    i = 0
    while (i > 127) or (i < 1):
        try:
            i = int(input("Enter ID # from 1-127: "))
        except ValueError:
            pass
    return i

# takes ID and returns doc from DB if exists. Returns empty string if not.
def checkID_DB(id):
    mongoclient = pymongo.MongoClient()
    db = mongoclient['FingerprintData']
    col = db['FingerTemplates']
    query = {"ID": id}    #define the criteria of our find
    result_query = list(col.find(query)) #retrieve from collection with specified query
    user = result_query[0]
    #print("Retrieved this from finger data in MongoDB: ", user) #just for debugging, really
    if user['name'] is None or user['name'] == "":
        print('You\'re not enrolled! Please see instructor about enrolling.')
        return {'Name': "failed"} #simply because this function must return a dict

    # package the name in a dictionary. Server will update student ID number
    #date = datetime.datetime.now().strftime("%m-%d-%Y")
    timenow = datetime.datetime.now()
    month = str(timenow.month)
    day = str(timenow.day)
    year = str(timenow.year)
    date = month + '/' + day + '/' + year
    #print("date is: ", date) #for debugging
    # server expects 'Name' rather than 'name' : take car of that here
    att_data = {'Name': user['name'], 'StudentIDNumber': 0, 'Date': date, 'Status': 'Present'}
    return att_data

def insert_student_DB(name, id):
    #insert to mongodb instance on fingerprint pi
    try:
        mongoclient = pymongo.MongoClient()
        db = mongoclient['FingerprintData']
        col = db['FingerTemplates']
        dict_to_insert = {'name': name, 'ID': id}
        res = col.insert_one(dict_to_insert)
        return True
    except:
        return False

def POST_dict(data):
    Auth = auth.HTTPBasicAuth('abc','123')
    destination = 'http://'+ IP_Address + ':8080/' + 'attendance'
    res = requests.post(url = destination, data = data,auth=Auth)
    if res.status_code == 200:
        return "good"
    elif res.status_code == 406:
        return "already in"
    else:
        return "error"

def enroll_student(info): #info_tuple contains name and ID used to enroll fingerprint
    if insert_student_DB(info['name'], info['ID']) == False:
        print("error while trying to insert student info to fingerprint pi's database")
        return False
    dict = {'Name': info['name'], 'StudentID': '123456789'}
    result_string = POST_enroll(dict)
    return result_string


def POST_enroll(data): #data is name and student ID number
    Auth = auth.HTTPBasicAuth('abc', '123')
    url = 'http://' + IP_Address + ':8080' + '/enroll'
    res = requests.post(url=url, data=data, auth=Auth)
    if res.status_code == 200:
        return "successfully enrolled"
    elif res.status_code == 406:
        return "already enrolled"
    else:
        return "error"

while True:
    red_LED()
    print("----------------")
    if finger.read_templates() != adafruit_fingerprint.OK:
        raise RuntimeError('Failed to read templates')
    print("Fingerprint templates:", finger.templates)
    print("e) enroll print")
    print("f) mark present")
    print("d) delete print")
    print("----------------")
    c = input("> ")

    if c == 'e':
        name = input('Enter your name: ')
        print('\n')
        id = get_num()
        info = {'name': name, 'ID': id}  # goes into local mongodb
        enroll_finger(id) #enrolls finger to the fingerprint reader
        print(enroll_student(info)) #inserts to local db, then posts to server to add student to master roster
    if c == 'f':
        if get_fingerprint():
            print("Detected #", finger.finger_id, "with confidence", finger.confidence)
            if finger.confidence > 100:
                yellow_LED()
                user=checkID_DB(finger.finger_id)
                #print("~~~~~~id is "+str(finger.finger_id)+" with input use name is "+str(user)+"~~~~~")
                status = POST_dict(user)
                if status == "good":
                    beep()
                    green_LED()
                    print("Counted Present")
                elif status == "already in":
                    print("Already counted present")
                else:
                    print('something wrong with post--')
            else:
                print("Try again")
        else:
            print("Finger not found")
    if c == 'd':
        if finger.delete_model(get_num()) == adafruit_fingerprint.OK:
            print("Deleted!")
        else:
            print("Failed to delete")
GPIO.cleanup()
