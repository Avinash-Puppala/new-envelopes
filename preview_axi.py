import requests

from pyaxidraw import axidraw   
ad = axidraw.AxiDraw()

# get output via: buffer.getvalue()

print("In here to be tested")

port = "/dev/cu.usbmodem1301"

path = "Casey/Pulsz/Envelopes/test.svg"
ad.plot_setup(path)
#ad.options.webhhook = True
ad.options.port = "/dev/cu.usbmodem1301"
#ad.options.webhhook_url = "https://webhook.site/a733efce-93ef-4878-b31a-40c7fa1a4c94"
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

ad.plot_run()
package = {
    "port": port,
    "path": path
}
x = requests.post("https://373a-24-53-138-18.ngrok.io", data=package)
print(x.text)

