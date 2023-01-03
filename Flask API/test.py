from urllib import response
import requests

BASE = "http://127.0.0.1:8080/"

data = {
    "Type":"Envelope"
}

data2 = {
    "file": "JesseG - Pulsz - Envelope 5.svg"
}

#response = requests.get(BASE + "set")
#response = requests.get(BASE + "get-next-plot/", json=data)
response = requests.post(BASE + "successful-plot/", json=data2)
#response = requests.post(BASE + "failed-plot/", json=data2)
print(response.content.decode())