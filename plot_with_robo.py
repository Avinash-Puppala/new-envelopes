import os, os.path, sys

import time

from pyaxidraw import axidraw   
ad = axidraw.AxiDraw()

import requests
from create_jwt_from_sa import generate_jwt

plot_type = sys.argv[2]
port = sys.argv[1]
file_to_plot = ""
folder_path = ""

# Paramters for JWT
sa_keyfile = "g_run/envelopes-370717-b88e05596a2e.json"
sa_email = "envelopes@envelopes-370717.iam.gserviceaccount.com"
expire = 3000  # you can set some integer
aud = "https://e-app-rmgdphogrq-uc.a.run.app"

# Create JWT
jwt = generate_jwt(sa_keyfile, sa_email, expire, aud)
# Header for Autheorizarion (Checked by Cloud Endpoint)
auth_header = {"Authorization": f"Bearer {jwt}"}

# Endpoint URL
url = "https://e-app-gateway-rmgdphogrq-uc.a.run.app"
# Name 
my_name = "Big Papi"

current_x = 0
current_y = 0

def move_into_position():

    #Connect to proper port
    ad.interactive()
    #ad.options.port = "/dev/cu.usbmodem1401"
    ad.options.port = port
    
    #IF AXIDRAW PLOTTER
    #PUT IN ALL PORTS HERE
    
    ad.options.pen_pos_up = 99
    

    ad.options.units = 2
    ad.connect()

    #Move Axi to proper position for next letter
    #ad.moveto(x,y)
    #ad.move(0,5)
    ad.move(5,0)

    #Disconnect
    ad.disconnect()
    print("Moving plotter complete.")

def move_plotter_home():

    iter_x = round(5.00,2)
    move_x = 0

    while iter_x > 0:

        move_x = 9

        if iter_x < 9:
            move_x = iter_x

        #Connect to proper port with settings
        ad.interactive()
        #ad.options.port = "/dev/cu.usbmodem1401"
        ad.options.port = port
        ad.options.units = 2
        
        #IF AXIDRAW PLOTTER
        #PUT IN ALL PORTS HERE
        
        ad.options.pen_pos_up = 99
        

        
        ad.params.start_pos_x = move_x
        ad.connect()
        ad.move((move_x*-1),0)
        ad.disconnect()
        time.sleep(0.25)
        

        print('Moving plotter home. Iteration: ' + str(move_x))

        iter_x = iter_x - 9
        

    #Move Axi to proper position for next letter
    #ad.moveto(x,y)

    """""
    to_move_x = round(5,2)

    #Connect to proper port
    ad.interactive()
    #ad.options.port = "/dev/cu.usbmodem1401"
    ad.options.port = port
    ad.options.units = 2
    ad.params.start_pos_y = to_move_x
    ad.connect()
    ad.move(0,to_move_x*-1)

    #Disconnect
    ad.disconnect()
    """
    print("Moving plotter complete.")
   
    print("Moving plotter first time to home complete.")
    exit()


def GoPlot():
    global port
    global file_to_plot
    global folder_path
    print("Printing to port "+ port)

    print("The path to plot is " +file_to_plot)
    print("The path with folder is " +folder_path+file_to_plot)

    ad.plot_setup(folder_path+file_to_plot)
    #set standard plotter options
    ad.options.speed_pendown = 85
    ad.options.speed_penup = 85
    ad.options.accel = 90

    #PEN UP/DOWN
    #AXIDRAW AND CHINESE PLOTTERS HAVE INVERTED UP/DOWN
    ad.options.pen_pos_down =  40
    ad.options.pen_pos_up = 60

    ad.options.pen_rate_lower = 90
    ad.options.pen_rate_raise = 90
    ad.options.pen_delay_down = 2
    ad.options.auto_rotate = False
    ad.options.reordering = 2
    ad.options.report_time = True
    #ad.options.random_start = True

    ad.options.port = port

    ad.plot_run()
    successful_plot()
    time.sleep(2)
    move_plotter_home()

def get_postal_code():
    print("Getting the postal code.")
    GoPlot()


# Sample file: Casey - Stake - Insert 25.svg
# Get Folder structure
def get_folder_from_file():
    global file_to_plot
    global folder_path

    client = file_to_plot.split(" - ")[0]
    site = file_to_plot.split(" - ")[1]
    plot_type = file_to_plot.split(" - ")[2].split(" ")[0]
    folder_path = folder_path + client + "/" + site + "/" + plot_type + "s/"

    if "take" in site:
        GoPlot()
    elif "lope" in plot_type and "ulsz" not in site:
        GoPlot()
    else:
        get_postal_code()


def get_next_plot():
    global file_to_plot
    global plot_type
    print("Getting next plot")
    
    # Make a request to the endpoint
    for header in [auth_header]:

        #fetch next file from cloud endpoint
        resp = requests.get(f"{url}/get-next-plot/{plot_type}", verify=True, headers=header)
        print(resp.content.decode())
        file_to_plot = resp.content.decode()[2:-1]
        get_folder_from_file()

def successful_plot():
    global file_to_plot
    print("Marking plot as successful")

    # Make a request to the endpoint
    for header in [auth_header]:
        #fetch next file from cloud endpoint
        resp = requests.get(f"{url}/successful-plot/{file_to_plot}", verify=True, headers=header)
        print(resp.content.decode())

move_into_position()
get_next_plot()