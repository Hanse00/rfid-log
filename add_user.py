import json
import sys
import argparse

from Phidgets.Devices.RFID import RFID
from Phidgets.PhidgetException import PhidgetException

def get_args():
    parser = argparse.ArgumentParser(description="Add a user to an rfid user list.")
    parser.add_argument("-d", "--debug", help="Debug flag", default=False, action="store_true")
    parser.add_argument("user_file", help="The json array storing the users.")

    args = vars(parser.parse_args())

    return args["debug"], args["user_file"]

def load_users(file_name):
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

def rfidError(e):
    print "Phidget error: %i, %s" % (e.eCode, e.description)

def rfidTagGained(e):
    print "Tag read!"

    if debug:
        print "Tag: %s" % e.tag
    rfid.setLEDOn(1)

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

def rfid_read(rfid):
    print "Scan tag, then press Enter."
    raw_input()

    try:
        print "Using tag: %s" % rfid.getLastTag()
        return rfid.getLastTag()
    except PhidgetException as e:
        print "Phidget error: %i, %s" % (e.code, e.details)
        exit(1)

def confirm():
    while True:
        conf = raw_input("[y]/[n]: ")
        if conf == "y":
            return True
        elif conf == "n":
            return False
        else:
            print "Please enter only y or n"

def get_user_name():
    while True:
        name = raw_input("Enter name: ")
        print "Are you sure you want to use: %s?" % name
        if confirm():
            if name == "":
                print "Name cannot be empty!"
                continue
            if debug:
                print "%s will be used!" % name
            return name

def add_user_to_list(user_list, tag, name):
    if debug:
        print "User list before adding: %s" % str(user_list)

    user = {"name": name, "tag": tag}
    user_list.append(user)

    if debug:
        print "After updating: %s" % str(user_list)

    return user_list

def wants_new_user():
    while True:
        print "Do you want to add another user?"
        if confirm():
            return True
        else:
            return False

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

def save_file(user_list, file_name):
    try:
        if debug:
            print "Saving file..."
        with open(file_name, "w") as f:
            json.dump(user_list, f, ensure_ascii=False, indent=4, sort_keys=True)
            if debug:
                print "File saved!"
    except IOError as e:
        print "IOError: %i, %s" % (e.errno, e.strerror)
        exit(1)

def main():
    global debug
    debug, file_name = get_args()

    user_list = load_users(file_name)

    global rfid
    rfid = init_rfid()

    while True:
        tag = rfid_read(rfid)
        user_name = get_user_name()
        user_list = add_user_to_list(user_list, tag, user_name)
        if not wants_new_user():
            break

    stop_rfid(rfid)
    save_file(user_list, file_name)

if __name__ == "__main__":
    main()