"""
Send a request to flask application
"""
import requests
from create_jwt_from_sa import generate_jwt

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
my_name = "Foo bar"

# Request 1) without header and 2) with header
for header in [auth_header]:
    # Method 1
    resp = requests.get(f"{url}/set", verify=True, headers=header)
    # resp = requests.get(f"{url}/get-next-plot/Envelope", verify=True, headers=header)
    # resp = requests.get(f"{url}/check-queues", verify=True, headers=header)
    # resp = requests.get(f"{url}/successful-plot/Casey - Stake - Insert 25.svg", verify=True, headers=header)
    # resp = requests.get(f"{url}/failed-plot/Casey - Stake - Insert 25.svg", verify=True, headers=header)
    print(resp.content.decode())
    #Remove first two characters and the last character from response
    file = resp.content.decode()[2:-1]
    print("File is: "+ str(file))
