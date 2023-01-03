import os, os.path, sys
import string

from datetime import date

import serial
from serial.tools import list_ports

import multiprocessing.dummy as mp 
import threading

import gspread
import pandas as pd

from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
from oauth2client.service_account import ServiceAccountCredentials

#define the scope
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

#add credentials to the service_account
creds = ServiceAccountCredentials.from_json_keyfile_name('pushin-the-envelope-4abefa15f15d.json',scope)

#authorize the clientsheet
client = gspread.authorize(creds)

gauth = GoogleAuth()
gauth.credentials = creds
drive = GoogleDrive(gauth)

sheet = client.open("Envelope Tracker")

tracker_worksheet = sheet.get_worksheet(1)
tracker_data = tracker_worksheet.get_all_records()
p_df = pd.DataFrame.from_dict(tracker_data)

who = ""
write_on = ""
site = ""

if sys.argv[1] is not None:
    who = sys.argv[1]
    who = who.replace("-", " ")
    write_on = sys.argv[2]
    site = sys.argv[3]
else:
    who, write_on, site = input("Who? E or I? Site?").split(",")

plot_path = ''

if who != "":
    who = who.rstrip().lstrip()
else:
    print("Please choose someone to write for. Try again.")
    exit()

if site != "":
    
    site = site.rstrip().lstrip()

    if site == "chumba":
        site = "Chumba"
    elif site == "gp":
        site = "GP"
    elif site == "puls" or site == "pulsz":
        site = "Pulsz"
    elif site =="ll":
        site = "LL"
else:
    site = "Pulsz"

if write_on != "":
    write_on = write_on.rstrip().lstrip()
    if write_on == "E" or write_on == "e" or write_on == "envelope" or write_on == "Envelope" or write_on == "Envelopes" or write_on == "envelopes":
        write_on = "Envelopes"
    else:
        write_on = "Inserts"
else:
    write_on = "Envelopes"

plot_path += who+"/"+site+"/"+write_on+"/"
print("plot path: "+plot_path)

_, _, files = next(os.walk(plot_path))
template_count = len(files) -1

print("Writing for: "+plot_path + "; for site: "+site+"; on "+write_on+"; with file count "+str(template_count))

plotter_ports = []

plotter_groups = [
    {"robo":"cu.usbmodem1401", "pos1":"", "pos2":"cu.usbmodem1301"}
]

for group in plotter_groups:

    group_info = group["robo"]+"/"+group["pos1"]+"/"+group["pos2"]
    ## open robo_group file
    ## pass the plotter_groups usb port into
    ## pass the info of what needs to be written
    os.system(f"python3 robo_group.py {group_info} {plot_path}")