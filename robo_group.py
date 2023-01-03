import os, os.path, sys

import gspread
import pandas as pd

import time

from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
from oauth2client.service_account import ServiceAccountCredentials

from pyaxidraw import axidraw   
ad = axidraw.AxiDraw()

from uarm import swift
from uarm.wrapper.swift_api import SwiftAPI

port = sys.argv[1]
print("Printing to port "+ str(port))

path_to_plot = sys.argv[2]
print("Path to plot is "+ path_to_plot)

#check if path has been given, if not let's figure out who to write for
#if its given, lets populate writers

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

##decide who to write for

##path assumes what to write is given
path_list = path_to_plot.split("/")

who = path_list[0]
site = path_list[1]
write_on = path_list[2]

_, _, files = next(os.walk(path_to_plot))
template_count = len(files) -1

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

print("Todays cell value: "+str(todays_value))

start_at = 1

#determine which templates to plot
if current_week_value > template_count:
    start_at = current_week_value % template_count
else:
    start_at = current_week_value

def place_envelopes():
    print("placing envelopes")

def estimate_plot_time():
    print("estimating envelope plot time")



count = 100

while count > 0:
    #place envelopes with the robo arm
    place_envelopes()

    #preview both plots and get the highest value
    wait_time = estimate_plot_time()

    #kick off each plot

    time.sleep(wait_time)

    #retrieve envelopes

    count = count - 1

    #update spreadsheet



#have robo set paper

#then have plotter kick off