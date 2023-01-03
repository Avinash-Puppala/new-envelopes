import asyncio

import subprocess
from subprocess import PIPE
  

async def plotters_run():
    i = 0

    while True:
        i += 1
        if i < 10:
            p = subprocess.Popen(["python3", "plotter1.py"])
            p2 = subprocess.Popen(["python3", "plotter2.py"])
            exitCode=p.wait()
            exitCode2=p2.wait()
              
            # New Line Added
            await asyncio.sleep(0.01)
    return 0
  
async def function_2():
    while True:
        await asyncio.sleep(0.01)
        print("\n HELLO WORLD \n")
  
loop = asyncio.get_event_loop()
asyncio.ensure_future(plotters_run())
asyncio.ensure_future(function_2())
loop.run_forever()
  
# You can also use High Level functions Like:
# asyncio.run(function_asyc())