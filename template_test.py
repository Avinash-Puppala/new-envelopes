import os
import pandas as pd

from pyaxidraw import axidraw   
ad = axidraw.AxiDraw()

plot_path = "Templates/Casey - GP - Envelopes New"

_, _, files = next(os.walk(plot_path))
template_count = len(files) - 1

print("Template count is: "+ str(template_count))

n = template_count

temp_dict = {}

while n > 0:

    file_to_print = plot_path+"/Casey - GP - Envelope "+ str(n) + ".svg"
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
    ad.options.preview = True

    ad.plot_run()

    time_estimate = ad.time_estimate 

    f_name = "Insert "+ str(n)
    temp_dict[f_name] = time_estimate

    n = n - 1

df = pd.DataFrame(temp_dict.items(), columns=["File", "Time"] )
print(df)

df.to_csv("Casey - GP - Envelopes New.csv", encoding='utf-8', index=False)


