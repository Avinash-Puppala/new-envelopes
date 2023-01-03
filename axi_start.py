import os, os.path, sys
import multiprocessing.dummy as mp 
import threading

plot_amount = 200
pod = "pod1"

if sys.argv[1] is not None:
    plot_amount = sys.argv[1]
    pod = sys.argv[2]
else:
    plot_amount, pod = input("How many plots? Pod?").split(",")

def run_conductor( plot_amount, pod):
    os.system("python3 conductor.py " + plot_amount + " " +pod )


#function to take user cli input selecting which pod to use and open conductor with the correct ports
def select_pod():
    global plot_amount
    global pod
    if pod:
        threading.Thread(target = run_conductor, args= (plot_amount, pod,)).start()
    else:
        print("Please select a valid pod and try again.")

select_pod()
   