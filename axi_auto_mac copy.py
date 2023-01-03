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

if __name__ == "__main__":
    for port in list_ports.comports():
        print(f"Name: {port.name}")
        print(f"Description: {port.description}")
        print(f"Location: {port.location}")
        print(f"Product: {port.product}")
        print(f"Manufacturer: {port.manufacturer}")
        print(f"ID: {port.pid}")
        if "USB" in port.hwid:
            print(f"Name: {port.name}")
            print(f"Description: {port.description}")
            print(f"Location: {port.location}")
            print(f"Product: {port.product}")
            print(f"Manufacturer: {port.manufacturer}")
            print(f"ID: {port.pid}")

            if(port.manufacturer == "Microsoft"):
                plotter_ports.append(port.name)

#get this weeks count for the template
row_to_pull = who + '-' + site+ '-'+ write_on
print("row to print is: "+row_to_pull)
#print(p_df)
#pulled_row = p_df.query("Type == 'Casey - GP - Inserts'")
#pulled_row = p_df.query("Type == 'CoreyGauss-Pulsz-Inserts'")
pulled_row = p_df.query("Type == @row_to_pull")
current_week_value = pulled_row['Current Week'].iloc[0]
print("Current Weeks Value: "+str(current_week_value))

column = tracker_worksheet.find("Current Week")
row = tracker_worksheet.find(row_to_pull)
column = string.ascii_uppercase[column.col - 1] 
row = row.row
cell = column+str(row)


#print("column is: "+string.ascii_uppercase[column.col]-1+" , row is: "+str(row.row))

start_at = 1

#determine which templates to plot
if current_week_value > template_count:
    start_at = current_week_value % template_count
else:
    start_at = current_week_value

pool_size = len(plotter_ports)  # your "parallelness"

def GoPlot(port, run):
    #print("Printing to port "+ port)

    singular_type = write_on.rstrip(write_on[-1])

    who2 = who.replace(" ", "!")

    file_name = who2 + "-" + site + "-" + singular_type +"!_"+ str(run) +"=.svg"
    #print("The chosen file is "+ file_name)

    path2 = plot_path.replace(" ", "!")

    file_to_print = path2 + file_name
    print("sending file path to plot of " +file_to_print)

    #os.system(f"python3 axi_automation_test2.py {port} {file_to_print}")
    


#pool = Pool(pool_size)

current_run = start_at
for plotter in plotter_ports:
    print("Current Run: "+str(current_run)+ "; and template count is: "+ str(template_count))
    
    #if current_run > start_at:
        #sleep((current_run-start_at)+1*3)

    if(current_run > template_count):
        current_run = 1
    else:
        current_run += 1
    threading.Thread(target = GoPlot, args= (plotter,current_run,)).start()
    current_week_value += 1
    #GoPlot(plotter, current_run)

#tracker_worksheet.update(cell, (current_week_value))
    

#pool.close()
#pool.join()

#Assign port
#You can specify the machine using the USB port enumeration (e.g., 
# COM6 on Windows or /dev/cu.usbmodem1441 on a Mac) or 
# by using an assigned USB nickname
#ad.options.port = "COM5"

#ad.plot_setup("Templates/Casey - Pulsez - Envelope Template1.svg")
#ad.plot_run()