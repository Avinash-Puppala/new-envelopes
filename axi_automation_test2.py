import os, os.path, sys

from pyaxidraw import axidraw   
ad = axidraw.AxiDraw()

import requests
from create_jwt_from_sa import generate_jwt

# Paramters for JWT
sa_keyfile = "/Users/caseygauss/Documents/Envelopes/g_run/pushin-the-envelope-4eb6601cb3bc.json"
sa_email = "envelopeproj@pushin-the-envelope.iam.gserviceaccount.com"
expire = 3000  # you can set some integer
aud = "https://g-run-v4-yng6lklq7a-uc.a.run.app"

# Create JWT
jwt = generate_jwt(sa_keyfile, sa_email, expire, aud)
# Header for Autheorizarion (Checked by Cloud Endpoint)
auth_header = {"Authorization": f"Bearer {jwt}"}

# Endpoint URL
url = "https://g-run-4-gateway-yng6lklq7a-uc.a.run.app"
# Name 
my_name = "Foo bar"

# Request 1) without header and 2) with header
for header in [auth_header]:
    # Method 1
    #resp = requests.get(f"{url}/set", verify=True, headers=header)
    resp = requests.get(f"{url}/get-next-plot/Insert", verify=True, headers=header)
    #resp = requests.get(f"{url}/check-queues", verify=True, headers=header)
    #resp = requests.get(f"{url}/successful-plot/Casey - Stake - Insert 25.svg", verify=True, headers=header)failed-plot
    #resp = requests.get(f"{url}/failed-plot/Casey - Stake - Insert 25.svg", verify=True, headers=header)
    print(resp.content.decode())


def GoPlot():
    port = sys.argv[1]
    print("Printing to port "+ port)

    file_to_print = sys.argv[2]
    #file_to_print = file_to_print.replace("-", " - ")
    file_to_print = file_to_print.replace("!", " ")
    file_to_print = file_to_print.replace("_", "(")
    file_to_print = file_to_print.replace("=", ")")
    print("The path to plot is " +file_to_print)

    ad.plot_setup(file_to_print)
    #set standard plotter options
    ad.options.speed_pendown = 85
    ad.options.speed_penup = 85
    ad.options.accel = 90
    ad.options.pen_pos_down = 30
    ad.options.pen_pos_up = 10
    ad.options.pen_rate_lower = 90
    ad.options.pen_rate_raise = 90
    ad.options.pen_delay_down = 2
    ad.options.auto_rotate = False
    ad.options.reordering = 2
    ad.options.report_time = True
    #ad.options.random_start = True

    ad.options.port = port

    ad.plot_run()


GoPlot()

#Assign port
#You can specify the machine using the USB port enumeration (e.g., 
# COM6 on Windows or /dev/cu.usbmodem1441 on a Mac) or 
# by using an assigned USB nickname
#ad.options.port = "COM5"

#ad.plot_setup("Templates/Casey - Pulsz - Envelope Template1.svg")
#ad.plot_run()