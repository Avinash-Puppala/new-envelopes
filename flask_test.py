from flask import Flask
from flask import request
from flask import json  #importing json cause that’s what we’re going to be working with

import os, sys

app = Flask(__name__)

@app.route('/', methods=['POST'])
def root():
    os.system(f"python3 preview_axi.py /dev/cu.usbmodem1301 Casey/Pulsz/Envelope1.svg")
    return 'Hello World!'

@app. route('/hooktest', methods=['POST'])  # ‘/hooktest’ specifies which link will it work on 
def hook_root():
    if request.headers['Content-Types'] == 'application/json':  # calling json objects
        return json.dumps(request.json)

if __name__ == '__main__':
  app.run(debug=True, port=5002)