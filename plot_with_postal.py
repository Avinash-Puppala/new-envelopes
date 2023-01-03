from glob import glob
import os, os.path, sys
from shutil import move
import random
import string

import  time

from tracemalloc import start

from pyaxidraw import axidraw   
ad = axidraw.AxiDraw()

from svgpathtools import svg2paths

import gspread
import pandas as pd

from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
from oauth2client.service_account import ServiceAccountCredentials

#Path and file
full_path = sys.argv[2]
#full_path = "Templates/Casey/Pulsz/Inserts/Casey - Pulsz - Insert 1.svg"

postal_code = sys.argv[3]

#Mac add "/dev/"
#PC remove "/dev/"
port = "/dev/"+sys.argv[1]

def movePlotterTo(x,y):

    global current_x, current_y

    print('Moving to...'+str(x)+" and y "+str(y))

    #Connect to proper port
    ad.interactive()
    #ad.options.port = "/dev/cu.usbmodem1401"
    ad.options.port = port
    ad.options.units = 2
    ad.connect()

    #Move Axi to proper position for next letter
    #ad.moveto(x,y)
    ad.move(x,0)
    ad.move(0,y)

    #Keep track of absolute position
    current_x += x
    current_y += y

    #Disconnect
    ad.disconnect()
    #print("Moving plotter complete.")

def movePlotterUp():
    #Connect to proper port
    ad.interactive()
    #ad.options.port = "/dev/cu.usbmodem1401"
    ad.options.port = port
    ad.connect()

    #Move Axi to up position
    ad.penup()

    #Disconnect
    ad.disconnect()
    print("Moving plotter up complete.")

def movePlotterHome():

    global total_distance
    global total_y

    global current_x
    global current_y

    global tallest_letter

    current_x = current_x + .5

    current_x = round(current_x,2)
    print("Should be moving to x of: "+ str(total_distance*-1))
    print("And y of: "+ str(total_y*-1))

    ##Axidraw will not move negative more than 10 points and I'm not sure why -_-
    ##So I am going to make it iterate 9mm over to home -_-

    iter_x = current_x

    while iter_x > 0:

        move_x = 9

        if iter_x < 9:
            move_x = iter_x

        #Connect to proper port with settings
        ad.interactive()
        #ad.options.port = "/dev/cu.usbmodem1401"
        ad.options.port = port
        ad.options.units = 2
        ad.params.start_pos_x = move_x
        ad.connect()
        ad.move((move_x*-1),0)
        ad.disconnect()
        time.sleep(0.25)

        iter_x = iter_x - 9
   
    print("Moving plotter first time to home complete.")

    ## Move to the proper verticle position

    #Connect to proper port
    ad.interactive()
    #ad.options.port = "/dev/cu.usbmodem1401"
    ad.options.port = port
    ad.options.units = 2
    ad.connect()

    move_y_to = tallest_letter + round(genRandFloat(1,5),2)
    ad.move(0,move_y_to)

    ad.disconnect()

def GoPlot(file_path, file):
    global port
    #port = sys.argv[1]
    #port = 'cu.usbmodem1401'

    file_to_print = file
    path_to_plot = file_path+file_to_print
    print("The path to plot is " +path_to_plot)

    ad.plot_setup(path_to_plot)
    #set standard plotter options
    ad.options.speed_pendown = 85
    ad.options.speed_penup = 85
    ad.options.accel = 90
    ad.options.pen_pos_down = 30
    ad.options.pen_pos_up = 70
    ad.options.pen_rate_lower = 90
    ad.options.pen_rate_raise = 90
    ad.options.pen_delay_down = 2
    ad.options.auto_rotate = False
    ad.options.reordering = 2
    #ad.options.report_time = True
    #ad.options.random_start = True
    ad.params.start_pos_x = 0
    ad.params.start_pos_y = 0

    #ad.options.port = "/dev/"+port
    #ad.options.port = "/dev/"+port
    ad.options.port = port

    output = ad.plot_run(True)
    ad.disconnect()

def genRandFloat(x,y):
    num = random.uniform(x, y)
    return round(num, 2) 

def fromPxtoMm(num):
    return round((num/3.81),2)

def fromMmtoPx(num):
    return round((num * 3.81),2)


def randomHorizontalSpacing():

    spacing = 10.00
    rando = genRandFloat(1,100)

    #range is 22px to 45px
    if rando < 70:
        #high probability
        spacing = genRandFloat(3,6)
    elif rando < 90:
        #mid probability
        #small gap
        spacing = genRandFloat(1,4)
    else:
        #low probability
        #larger gap
        spacing = genRandFloat(7,14)


    return round(spacing/3.83,2)

def randomVerticleSpacing():

    #eventually may want to make this so that the 
    # proceeding numbers have a similar verticle position
    
    spacing = 0.1
    rando = genRandFloat(1,100)
    rando2 = genRandFloat(1,100)

    #range -1 - 6
    #average is going to be -0.5 to 1
    if rando < 80:
        #high probability
        spacing = genRandFloat(0,0.3)
    elif rando < 90:
        spacing = genRandFloat(0.3, 5)
    else:
        #mid probability that it's negative
        spacing = genRandFloat(0,1)
        spacing = spacing * -1

    return round(spacing/3.83, 2)


def calculateSizeForFilePath(file):
    paths, attributes = svg2paths(f'Templates/PostalCodes/{file}')

    # let's take the first path as an example
    mypath = paths[0]

    # Let's find its length
   # print("length = ", mypath.length())

    # Find height, width in mm
    xmin, xmax, ymin, ymax = mypath.bbox()
    width = (xmax - xmin)
    height = (ymax - ymin)
    #print("width = ", width)
    #print("height = ", height)

    return [height, width]

num = 0
base_y = fromPxtoMm(genRandFloat(3,8))
tallest_letter = 0

#print("Base y is going to be: "+str(base_y))

def plot_postal_code():
    global postal_code
    global num
    global base_y
    global list_of_widths
    global total_width
    global total_y
    global last_width
    global total_distance
    global file_to_plot

    global current_x
    global current_y

    global tallest_letter

    code_string = str(postal_code)

    folder_count = 0  # type: int
    input_path = "Templates/PostalCodes/"  # type: str
    for folders in os.listdir(input_path):  # loop over all files
        if os.path.isdir(os.path.join(input_path, folders)):  # if it's a directory
            folder_count += 1  # increment counter

    #set_num = random.randint(1,folder_count)

    ##Get file's ending digit
    ending_file_digit = file_to_plot.split('.')[0]
    ending_file_digit = int(ending_file_digit[-1])

    set_to_use = 1

    if folder_count > 1:
        set_to_use = ending_file_digit % folder_count
        set_to_use += 1
    else:
        set_to_use = 1

    #Keep track of the digits used so we don't repeat
    digits_used_list = []

    #Run through the postal codes
    for digit in code_string:

        digits_used_list.append(digit)

        current_count = digits_used_list.count(digit)

        ###########
        ## CHANGE HERE BASED ON HOW MANY REPEAT DIGITS YOU HAVE IN EACH SET ##
        ## If you have four of each digit, the number below should be 5 for example
        ###########
        if current_count == 5:
            current_count = 1

        #Example naming convention Set1/Set1 - 4 - 6.svg

        file_name = f"Set{set_to_use}/Set{set_to_use} - {current_count} - "+str(digit)+".svg"
        print("Getting digit file name of: "+file_name)

        r_width = calculateSizeForFilePath(file_name)[1]
        r_height = calculateSizeForFilePath(file_name)[0]

        print("Width is: "+str(r_width))
        if r_height > tallest_letter:
            tallest_letter = round(r_height,2)

        list_of_widths.append(r_width)
        
        #always going to start around 5px
        spacing = 0
        start_x = 0
        start_y = 0

        if num != 0:
            ## Not the first time running through

            #Get spacing before
            spacing = randomHorizontalSpacing()
            #print("Horizontal spacing is: "+ str(spacing))
            start_x = round(last_width + spacing, 2)

            start_y = randomVerticleSpacing()
        else:
            ## First time running through
            spacing = genRandFloat(5,10)
            spacing = round(spacing/3.83,2)
            start_x = spacing

            start_y = base_y
            total_y = base_y

        print("Spacing is: "+str(spacing))
        
        #print("Vert spacing is " + str(vert))
        total_y = total_y + start_y

        print("Start X is: "+str(start_x) + " and the start y is: "+ str(start_y))

        #Generate semi-random spacing
        #spacing = genRand()

        #Testing no verticle change
        movePlotterTo(start_x,start_y)
        #time.sleep(1)
        GoPlot("Templates/PostalCodes/", file_name)

        #Print out each SVG
        total_width = total_width + r_width
        total_distance = total_distance + r_width + spacing
        print("Total width is now: "+str(total_width))
        num = num + 1
        last_width = r_width

def plot_file():
    global file_to_plot
    global folder_path

    movePlotterHome()
    time.sleep(2)
    GoPlot(folder_path, file_to_plot)
    
plot_postal_code()
plot_file()
