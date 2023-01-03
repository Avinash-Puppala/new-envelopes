import asyncio
import sys

import subprocess
from subprocess import PIPE
import time

#create a global dictionary containing two plotters and one robot arm
pod_dict = {
    "pod1": {
        "robot": "COM26",
        "plotter1": "COM4",
        "plotter2": "COM6",
        "type": "Envelope",
        "full": 600,
        "half": 100,
        "numberOfPlotters": 2, 
        "numberOfStacks": 2
    },
    "pod2": {
        "robot": "COM26",
        "plotter1": "COM4",
        "plotter2": "COM6", 
        "type": "Envelope",
        "full": 300,
        "half": 175,
        "numberOfPlotters": 2,
        "numberOfStacks": 1
    }
}

#given_amount = sys.argv[1]
pod = sys.argv[2]

plotter1 = pod_dict[pod]["plotter1"]
plotter2 = pod_dict[pod]["plotter2"]
plot_type = pod_dict[pod]["type"]
robot = pod_dict[pod]["robot"]
plot_amount = int(sys.argv[1])
current_count = 0
  
  
async def plotters_run():
    
    #subprocess popen with parameters
    #plotter 1
    p = subprocess.Popen(["python", "plot_with_robo.py", plotter1, plot_type])

    #plotter 2
    if plotter2 != "none":
        p2 = subprocess.Popen(["python", "plot_with_robo.py", plotter2, plot_type])

    exitCode=p.wait()

    if plotter2 != "none":
        exitCode=p2.wait()
              
    # New Line Added
    return 0
  
async def function_2(type):
    global current_count

    #run robot arm code 
    if type == "place":
        print("Placing now")
        rp = subprocess.Popen(["python", "uArm-Python-SDK/examples/test/run_robo.py", "place", plot_type, pod, str(current_count)])
        exitCode=rp.wait()
    elif type == "remove":
        print("Removing")
        rp2 = subprocess.Popen(["python", "uArm-Python-SDK/examples/test/run_robo.py", "remove", plot_type, pod, str(current_count)])
        exitCode=rp2.wait()
    
    return 0
  
async def main():
    global current_count
    global plot_amount

    while current_count < plot_amount:

        print("Current count is " + str(current_count))
        print("Plot amount is " + str(plot_amount))
        
        if current_count == 0:
            f2 = loop.create_task(function_2("place"))
            f1 = loop.create_task(plotters_run())

            #Removes and places the envelope/insert
            f3 = loop.create_task(function_2("remove"))

            await asyncio.wait([f2, f1, f3])
        else:
            f1 = loop.create_task(plotters_run())

            #Removes and places the envelope/insert
            f3 = loop.create_task(function_2("remove"))

            await asyncio.wait([f1, f3])
            

        current_count += 2
  
# to run the above function we'll 
# use Event Loops these are low 
# level functions to run async functions
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
