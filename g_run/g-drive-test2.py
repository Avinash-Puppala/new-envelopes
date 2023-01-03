import os

from flask import Flask, render_template, request
from flask_cors import CORS
from flask_sslify import SSLify
#from flask_sqlalchemy import SQLAlchemy

from webargs import fields
from webargs.flaskparser import use_args

from datetime import date, timedelta

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

r = redis.Redis(host='localhost', port=6379, db=1)
#q = Queue(connection=r)

##setup logic for getting G Sheet info

#define the scope of G Sheets
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

#add credentials to the service_account
creds = ServiceAccountCredentials.from_json_keyfile_name('../pushin-the-envelope-4abefa15f15d.json',scope)

#authorize the clientsheet
client = gspread.authorize(creds)

gauth = GoogleAuth()
gauth.credentials = creds
drive = GoogleDrive(gauth)

sheet = client.open("Envelope Tracker")

tracker_worksheet = sheet.get_worksheet(1)
tracker_data = tracker_worksheet.get_all_records()
p_df = pd.DataFrame.from_dict(tracker_data)

people_ids={}
folder_ids={}
file_ids={}
subfolder_ids={}
file_names={}

pname_to_id={}
name_to_id={}
subname_to_id={}
master_dic={"Casey":{}}

def search_file():

    try:
        # create drive api client
        service = build('drive', 'v3', credentials=creds)
        files = []
        page_token = None
        while True:
            # pylint: disable=maybe-no-member
            # begin search at the Completed Templates level
            response = service.files().list(q="mimeType='application/vnd.google-apps.folder' and '1UcSEzJTTAaaWLE8IT3FTinlyzkc5AuV_' in parents",
                                     spaces='drive',
                                     fields='nextPageToken, files(id, name)').execute()

            templates = response.get('files', [])

            if not templates:
                print('none')
                return None

            #cycle through the client folders first
            for person in templates:
                pname_to_id[person['id']] = person['name']
                print("Looking for: "+person.get('name'))
                people_ids[person['id']]=person['id']

            for person_id in people_ids:
                items = service.files().list(q=f"mimeType = 'application/vnd.google-apps.folder' and '{person_id}' in parents", fields='nextPageToken, files(id, name)').execute()

                person_dict = {}
                person_name = pname_to_id[person_id]

                #site folders
                for item in items.get('files', []):
                    print('found folder: '+item.get('name'))
                    name_to_id[item['id']] = item['name']
                    folder_ids[item['id']]=item['id']

                #request envelope and insert folders
                for folder_id in folder_ids:
                    print('looking in folder with id: '+folder_id)
                    subfolders = service.files().list(q=f"mimeType = 'application/vnd.google-apps.folder' and '{folder_id}' in parents", fields='nextPageToken, files(id, name)').execute()
                    
                    site_dict = {}
                    site_name = name_to_id[folder_id]

                    for sfold in subfolders.get('files', []):
                        print("found subfolder: "+sfold['name'])
                        subname_to_id[sfold['id']] = sfold['name']
                        subfolder_ids[sfold['id']]=sfold['id']

                    for subfolder_id in subfolder_ids:
                        children = service.files().list(q=f" mimeType = 'image/svg+xml' and '{subfolder_id}' in parents", fields='nextPageToken, files(id, name)').execute()

                        child_count = len(children.get('files', []))
                        site_dict[subname_to_id[subfolder_id]] = children
                        site_dict[subname_to_id[subfolder_id] + "_count"] = child_count

                        for child in children.get('files', []):
                            file_ids[child['id']]=child['id']
                            file_names[child['name']]=child['name']
                            #print(F'Found file: {child.get("name")}')

                    person_dict[site_name] = site_dict
                master_dic[person_name] = person_dict
            
            return file_ids

    except HttpError as error:
        print(F'An error occurred: {error}')
        files = None

    return files

search_file()
print(master_dic)

#def count_files_in_folder():
   # folder = DriveApp
