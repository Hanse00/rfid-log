# -*- coding: utf-8 -*-

import argparse
import json
import sys
import datetime
import codecs

from Phidgets.Devices.RFID import RFID
from Phidgets.PhidgetException import PhidgetException

def get_args():
    parser = argparse.ArgumentParser(description="Add a user to an rfid user list.")
    parser.add_argument("-d", "--debug", help="Debug flag", default=False, action="store_true")
    parser.add_argument("user_file", help="The json array storing the users.")
    parser.add_argument("log_file", help="The file to store logs in.")

    args = vars(parser.parse_args())

    return args["debug"], args["user_file"], args["log_file"]

def load_file(file_name):
    try:
        if debug:
            print "Opening file..."
        with open(file_name, "r") as f:
            if debug:
                print "File open!"
            return json.load(f)
    except ValueError as e:
        #The file opened was not a valid JSON file
        print "File error: %s stopping!" % e
        exit(1)
    except IOError as e:
        #Error 2 is "no such file or directory"
        #Make a new file, return an empty list
        if e.errno == 2:
            return []
        else:
            print "IOError: %i, %s" % (e.errno, e.strerror)
            exit(1)

def get_name_from_tag(tag):
    for dic in user_list:
        if dic["tag"] == tag:
            return dic["name"]
    return "None"

def save_to_log(date, time, name):
    log_list = load_file(log_file)

    log_obj = {"date": date, "time": time, "name": name}
    log_list.append(log_obj)

    try:
        with codecs.open(log_file, "w", "UTF-8") as f:
            json.dump(log_list, f, ensure_ascii=False, indent=4)
            if debug:
                print "Saved to log!"
    except IOError as e:
        print "IOError: %i, %s" % (e.errno, e.strerror)
        exit(1)


def log_tag(tag):
    date = str(datetime.datetime.today().date())
    time = datetime.datetime.now().strftime("%H:%M:%S")
    name = get_name_from_tag(tag)

    if debug:
        print date, time, name

    save_to_log(date, time, name)

def rfidError(e):
    print "Phidget error: %i, %s" % (e.eCode, e.description)

def rfidTagGained(e):
    if debug:
        print "Tag: %s" % e.tag
    rfid.setLEDOn(1)

    log_tag(e.tag)

def rfidTagLost(e):
    rfid.setLEDOn(0)

def init_rfid():
    try:
        if debug:
            print "Initializing RFID object..."
        rfid = RFID()

        rfid.setOnErrorhandler(rfidError)
        rfid.setOnTagHandler(rfidTagGained)
        rfid.setOnTagLostHandler(rfidTagLost)

        rfid.openPhidget()

        if debug:
            print "RFID object initialized!"
            print "Waiting to attach RFID reader..."

        rfid.waitForAttach(10000)

        if debug:
            print "RFID reader attached!"

        rfid.setAntennaOn(True)

        return rfid
    except RuntimeError as e:
        print "Runtime error: %s stopping!" % e.details
        exit(1)
    except PhidgetException as e:
        print "Phidget error: %i, %s" % (e.code, e.details)
        exit(1)

def stop_rfid(rfid):
    try:
        if debug:
            print "Stopping RFID..."
        rfid.closePhidget()
        if debug:
            print "RFID stopped!"
    except PhidgetException as e:
        print "Phidget error: %i, %s" % (e.code, e.details)
        exit(1)

def main():
    global debug, log_file
    debug, user_file, log_file = get_args()

    global user_list
    user_list = load_file(user_file)

    global rfid
    rfid = init_rfid()

    raw_input("Press Enter to stop.\n")

    stop_rfid(rfid)

if __name__ == "__main__":
    main()