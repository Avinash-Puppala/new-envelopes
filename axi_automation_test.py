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
creds = ServiceAccountCredentials.from_json_keyfile_name('pushin-the-envelope-975f619f171a.json',scope)

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
    elif site =="stake" or site == "Stake" or site == "s" or site == "S":
        site = "Stake"
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
#print("plot path: "+plot_path)

print("Plot path is: Templates/"+plot_path)

_, _, files = next(os.walk("Templates/"+plot_path))
template_count = len(files)

print("Writing for: "+plot_path + "; for site: "+site+"; on "+write_on+"; with file count "+str(template_count))

plotter_ports = []

if __name__ == "__main__":
    for port in list_ports.comports():
        if "USB" in port.hwid:
            #print(f"Name: {port.name}")
            #print(f"Description: {port.description}")
            #print(f"Location: {port.location}")
            #print(f"Product: {port.product}")
            #print(f"Manufacturer: {port.manufacturer}")
            #print(f"ID: {port.pid}")

            if(port.manufacturer == "SchmalzHaus LLC"):
                plotter_ports.append(port.name)

#get this weeks count for the template
row_to_pull = who + ' - ' + site+ ' - '+ write_on

#print("row to pull: " + row_to_pull)
#print(p_df)
pulled_row = p_df.query("Type == @row_to_pull")
current_week_value = pulled_row['Current Week'].iloc[0]
print("Current Weeks Value: "+str(current_week_value))

column = tracker_worksheet.find("Current Week")
row = tracker_worksheet.find(row_to_pull)
column = string.ascii_uppercase[column.col - 1] 
row = row.row
cell = column+str(row)

#print("cell is : "+ cell)

today = date.today()

# get todays date and corresponding cell value
year = today.strftime("%Y")
abv_year = year[-2:]
today_date = today.strftime("%m/%d/")+abv_year
#print("Todays date: ", today_date)

todays_value = pulled_row[str(today_date)].iloc[0]
today_col = tracker_worksheet.find(str(today_date))
today_col = string.ascii_uppercase[today_col.col - 1]
today_cell = today_col+str(row)

if todays_value == "":
    todays_value = 0

if current_week_value == "":
    current_week_value = 0

print("Todays cell value: "+str(todays_value))

start_at = 1 

#determine which templates to plot
if current_week_value > template_count:
    start_at = current_week_value % template_count
else:
    start_at = current_week_value

def getPostalCodes(number, file):

    print(f"Getting {str(number)} postal codes for {file}....")

    global client

    sheet_name = " Postal Code Tracker"
    sheet_prefix = ''

    if 'Pulsz' in file:
        sheet_prefix = 'Pulsz'
    elif 'GP' in file:
        sheet_prefix = 'GP'
    elif 'Chumba' in file:
        sheet_prefix = 'Chumba'
    elif 'LL' in file:
        sheet_prefix = 'LL'

    plot_type = "Insert"

    if 'Envelope' in file:
            plot_type = "Envelope"

    ws_name = file.split('-')[0]

    if ws_name[-1] == ' ':
        ws_name = ws_name[:-1]


    sheet_name = sheet_prefix + sheet_name

    print("Worksheet name: "+ws_name)
    print("Sheet name:"+sheet_name)

    p_sheet = client.open(sheet_name)

    tracker_ws = p_sheet.worksheet(ws_name)
    t_data = tracker_ws.get_all_records()
    postal_df = pd.DataFrame.from_dict(t_data)

    querying_for = "Used "+ plot_type
    print("Querying for "+ querying_for)

    postal_df = postal_df[postal_df[querying_for] != 'Used']

    #p_df = p_df.query("@querying_for != True")

    #codes = postal_df["Base64 Image"]
    count = 0
    list_of_codes = []

    for index in postal_df.index:

        print("Getting "+number+" of codes.")
        while count < number:
            code = postal_df.loc[index,'Base64 Image']
            list_of_codes.append(code)

            print("The postal code is "+code)


            column = tracker_ws.find(querying_for)
            row = tracker_ws.find(str(code))
            column = string.ascii_uppercase[column.col - 1] 
            row = row.row
            cell = column+str(row)
            tracker_ws.update(cell, "Used")

            count = count + 1

    return list_of_codes

getPostalCodes(len(plotter_ports),plot_path) 

def GoPlot(port, run):
    #print("Printing to port "+ port)

    last_letter = write_on[-1]
    singular_type = write_on

    #run = run -1 


    if last_letter == "s":
       singular_type = write_on.rstrip(write_on[-1])

    who2 = who.replace(" ", "!")

    file_name = who + "-" + site + "-" + singular_type +"!"+ str(run) +".svg"
    #print("The chosen file is "+ file_name)

    path2 = plot_path.replace(" ", "!")

    file_to_print = path2 + file_name
    print("Print to port: " +port + " with template named: " +file_to_print)

    os.system(f"python3 axi_automation_test2.py {port} {file_to_print}")

current_run = start_at
for plotter in plotter_ports:
    print("Running THE loop")
    #print("Current Run: "+str(current_run)+ "; and template count is: "+ str(template_count))
    if current_run > template_count:
        current_run = 1
    elif current_run != template_count:
       current_run += 1

    #threading.Thread(target = GoPlot, args= (plotter,current_run,)).start()
    if current_run == template_count:
        current_run += 1

    current_week_value += 1
    todays_value += 1

tracker_worksheet.update(cell, (current_week_value))
tracker_worksheet.update(today_cell, (todays_value))