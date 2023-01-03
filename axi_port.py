
from serial.tools import list_ports

plotter_ports = []

if __name__ == "__main__":
    for port in list_ports.comports():
        if "USB" in port.hwid:
            print(f"Name: {port.name}")
            print(f"Description: {port.description}")
            print(f"Location: {port.location}")
            print(f"Product: {port.product}")
            print(f"Manufacturer: {port.manufacturer}")
            print(f"ID: {port.pid}")

            if(port.manufacturer == "SchmalzHaus LLC"):
                plotter_ports.append(port.name)