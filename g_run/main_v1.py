from hashlib import new
import string
import os

from flask import Flask, render_template, request
from flask_cors import CORS
from flask_sslify import SSLify
#from flask_sqlalchemy import SQLAlchemy

from webargs import fields
from webargs.flaskparser import use_args

from datetime import date, datetime, timedelta
from pytz import timezone
#import timeit

import redis

from rq import Queue
from rq.job import Job
#from redis_worker import conn

import gspread
import pandas as pd

from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.service_account import ServiceAccountCredentials

# Initialise flask app
app = Flask(__name__)
#CORS(app, supports_credentials=True)
#sslify = SSLify(app)

#app.config.from_object(os.environ['APP_SETTINGS'])
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
#db = SQLAlchemy(app)

#q = Queue(connection=conn)

#r = redis.Redis(host='localhost', port=6379, db=1)
r = redis.Redis(host='10.32.86.131', port=6379, db=1)
redis_host = os.environ.get('REDISHOST', 'localhost')
redis_port = int(os.environ.get('REDISPORT', 6379))
r = redis.StrictRedis(host=redis_host, port=redis_port)
#q = Queue(connection=r)

##setup logic for getting G Sheet info

#define the scope of G Sheets
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

#add credentials to the service_account 
#creds = ServiceAccountCredentials.from_json_keyfile_name('../pushin-the-envelope-4abefa15f15d.json',scope)
creds = ServiceAccountCredentials.from_json_keyfile_name('envelopes-370717-b88e05596a2e.json',scope)

#authorize the clientsheet
client = gspread.authorize(creds)

gauth = GoogleAuth()
gauth.credentials = creds
drive = GoogleDrive(gauth)

sheet = client.open("Envelopes Tracker")

tracker_worksheet = sheet.get_worksheet(1)
tracker_data = tracker_worksheet.get_all_records()
p_df = pd.DataFrame.from_dict(tracker_data)

folder_ids={}
file_ids={}

redis_envelope_queue = []
redis_insert_queue = []

redis_envelope_retry = []
redis_insert_retry = []

#storing redis values as
# envelope_queue
# insert_queue

# retry_envelopes
# retry_inserts

# envelope_queue_count
# insert_queue_count


def if_zero(value):
    if value == None or value == '':
         return 0
    else: 
        return int(value)

def run_through_rows(pd_obj, first_50, skip_50):

    global redis_envelope_queue
    global redis_insert_queue

    for index, row in pd_obj.iterrows():
        #pulsz_env_rows = 
        #pulsz_ins_rows = 
        t_type = row["Type"]
        t_count = if_zero(row["Templates"])
        t_goal = if_zero(row["Weekly Target"])
        t_current = if_zero(row["Current Week"])

        base_date = datetime.now(timezone("US/Eastern"))

        year = base_date.strftime("%Y")
        abv_year = year[-2:]
        t_date = base_date.strftime("%m/%d/")+abv_year
        #t_date = str(t_date)

        d_current = row[t_date]

        file_name = t_type[:-1]

        #act like the goal is only 50 so that it will prioritize everyone's first 50 on GP and Chumba
        if first_50:
            t_goal = 50
        
        # skip the first 50
        if skip_50:
            t_current = 50

        c_count = int(t_current)
        
        #add to envelope queue
        while c_count < t_goal and t_count > 0:
            
            file_num = c_count % t_count

            if file_num == 0:
                file_num = t_count

            complete_file_name = file_name+" "+str(file_num)+".svg"

            if "Envelope" in str(t_type):
                redis_envelope_queue.append(complete_file_name)
            else:
                redis_insert_queue.append(complete_file_name)
            #print("Left to write this week: "+complete_file_name)

            c_count = c_count + 1

        #print(f"{t_type} has {str(t_goal -t_current)} emaining Pulsz to plot." )


def set_template_prioritization():
    global redis_envelope_queue
    global redis_insert_queue
    #plot all Stake then Pulsz targets starting top to bottom
    #then 50 of each GP and Chumba
    #then the rest of GP and Chumba
    
    #pull all rows to organize for Pulsz site first
    print("Setting Stake")
    stake_rows = p_df[p_df['Type'].str.contains(r'Stake(?!$)')]
    run_through_rows(stake_rows, False, False)
    print("Setting Pulsz")
    pulsz_rows = p_df[p_df['Type'].str.contains(r'Pulsz(?!$)')]
    run_through_rows(pulsz_rows, False, False)
    print("Pulsz is set")
    gp_and_chumba = p_df[p_df['Type'].str.contains(r'GP|Chumba')]
    run_through_rows(gp_and_chumba, True, False)
    run_through_rows(gp_and_chumba, False, True)

    r.rpush('envelope_queue', *redis_envelope_queue)
    r.rpush('insert_queue', *redis_insert_queue)

    r.set('insert_queue_count', len(redis_insert_queue))
    r.set('envelope_queue_count', len(redis_envelope_queue))

    #print("Envelope Queue:")
    #print(r.lrange('envelope_queue', 0, -1))

    #r.rpush('retry_envelopes', *[])
    #r.rpush('retry_inserts', *[])

    return f"Queues set - Envelopes Left: {len(redis_envelope_queue)}; and Inserts Left: {len(redis_insert_queue)}"


#set_template_prioritization()

print("Remaining plots this week:")
print("Envelopes: "+str(len(redis_envelope_queue)))
print("Inserts: "+str(len(redis_insert_queue)))


def set_queues():
    set_template_prioritization()

    return "Done"

def get_next_plot(type):
    #type = envelope or isnert

    next_file = ""

    if type == 'Envelope':
        # Check first if there is a file that needs redone
        if  r.llen('retry_envelopes')> 0:
            next_file = r.lpop('retry_envelopes')
        else:
            #next_list = r.get('envelope_queue')
            #next_file = next_list[0]
            #next_list.pop(0)
            #r.lpush('envelope_queue', next_list)
            next_file = r.lpop('envelope_queue')
            r.set('envelope_queue_count', r.llen('envelope_queue'))
    else:
        #check first if there are files to retry
        if r.llen('retry_inserts') > 0:
            next_file = r.lpop('retry_inserts')
        else:
            #next_list = r.get('insert_queue')
            #next_file = next_list[0]
            #next_list.pop(0)
            #r.set('insert_queue', next_list)
            #count = r.get('insert_queue_count')
            next_file = r.lpop('insert_queue')
            r.set('insert_queue_count', r.llen('insert_queue'))

    #look for specified account or website
    #timeit.timeit('next((s for s in mylist if sub in s), None)', setup='from __main__ import mylist, sub', number=100000)

    return next_file

def formatted_date():
    base_date = datetime.now(timezone("US/Eastern"))

    year = base_date.strftime("%Y")
    abv_year = year[-2:]
    t_date = base_date.strftime("%m/%d/")+abv_year

    return t_date

def failed_plot(file):
    if "Envelope" in file:
        r.rpush('retry_envelopes', file)
    else:
        r.rpush('retry_inserts', file)

    #decrease today and total count in the tracking sheet, but it'll take a min to parse lol
    fd = formatted_date()

    line_name = format_file_to_lineItem(file)

    pulled_row = p_df.query("Type == @line_name")
    current_week_value = pulled_row['Current Week'].iloc[0]
    current_week_value = if_zero(current_week_value)

    column = tracker_worksheet.find("Current Week")
    row = tracker_worksheet.find(line_name)
    column = string.ascii_uppercase[column.col - 1] 
    row = row.row
    cell = column+str(row)

    todays_value = pulled_row[fd].iloc[0]
    today_col = tracker_worksheet.find(fd)
    today_col = string.ascii_uppercase[today_col.col - 1]
    today_cell = today_col+str(row)
    todays_value = if_zero(todays_value)

    tracker_worksheet.update(cell, (current_week_value - 1))
    tracker_worksheet.update(today_cell, (todays_value - 1))

    return "Marked as failed and added to queue to retry."

    #send notification that a plot failed


def end_of_the_road(hub_id):
    ##send alert letting operator know that a hub has run through its materials
    a=1
    print("Plotted out")

def format_file_to_lineItem(file):

    rFile = file[:-6]
    last_c = rFile[len(rFile) - 1]

    if last_c == "e":
        rFile = rFile+"s"
    else:
        rFile = rFile[:-1]
        rFile = rFile +"s"
    
    return rFile

def successful_plot(file):

    fd = formatted_date()

    line_name = format_file_to_lineItem(file)

    pulled_row = p_df.query("Type == @line_name")
    current_week_value = pulled_row['Current Week'].iloc[0]

    column = tracker_worksheet.find("Current Week")
    row = tracker_worksheet.find(line_name)
    column_v = string.ascii_uppercase[column.col - 1] 
    row_v = row.row
    cell = column_v+str(row_v)

    todays_value = pulled_row[fd].iloc[0]
    today_col = tracker_worksheet.find(fd)
    today_col = string.ascii_uppercase[today_col.col - 1]
    today_cell = today_col+str(row_v)

    new_week_val = if_zero(current_week_value) + 1
    new_val = if_zero(todays_value) + 1

    m_row = row_v - 2

    #Need to set the value in the pandas df as well
    p_df.at[m_row, "Current Week"] = new_week_val
    p_df.at[m_row, fd] = new_val

    tracker_worksheet.update(cell, new_week_val)
    tracker_worksheet.update(today_cell, new_val)

    return "Success!"
    

def check_queue_count():
    e_count = r.get('envelope_queue_count')
    i_count = r.get('insert_queue_count')

    return f"Remain Envelope Count: {e_count}, and Insert Count: {i_count}"

@app.route("/set", methods=["GET"])
def setQueues():
    r.flushdb()
    r.flushall()
    #Trigger to set queue 
    print("Set request received")
    response = set_queues()

    return f"Success: {response}", 200

@app.route("/check-queues", methods=["GET"])
def checkQueues():
    #Trigger to get queue count to make sure its working
    response = check_queue_count()

    return f"Success: {response}", 200

@app.route("/get-next-plot/<plot_type>", methods=["GET"])
def getNextPlot(plot_type):
    #Trigger to get queue count to make sure its working
    #person = request.json["Person"]
    #site = request.json['Site']
    response = get_next_plot(plot_type)

    return f"{response}", 200

@app.route("/successful-plot/<plot_file>", methods=["GET"])
def successfulPlot(plot_file):
    #Trigger to get queue count to make sure its working

    response = successful_plot(plot_file)

    return f"{response}", 200

@app.route("/failed-plot/<failed_file>", methods=["GET"])
def failedPlot(failed_file):
    #Trigger to get queue count to make sure its working

    response = failed_plot(failed_file)

    return f"{response}", 200

"""""
NEED TO ADD TO YAML
@app.route("/flush-redis", methods=["GET"])
def flushRedis():
    #Trigger to get queue count to make sure its working
    r.flushdb()
    r.flushall()

    return "Successfully flushed", 200

"""



@app.route("/")
def top_page():
    """top_page"""
    return "Welcome to my application, version 1\n"


if __name__ == "__main__":
    app.run( host="0.0.0.0", port=8080)
