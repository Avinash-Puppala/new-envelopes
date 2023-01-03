"""
Send a request to flask application
"""
import requests
from create_jwt_from_sa import generate_jwt

""""
# Paramters for JWT
sa_keyfile = "/Users/caseygauss/Documents/Envelopes/g_run/pushin-the-envelope-a0134d24ac9d.json"
sa_email = "envelopeproj@pushin-the-envelope.iam.gserviceaccount.com"
expire = 3000  # you can set some integer
aud = "https://g-run-v2-yng6lklq7a-uc.a.run.app"

# Create JWT
jwt = generate_jwt(sa_keyfile, sa_email, expire, aud)
# Header for Autheorizarion (Checked by Cloud Endpoint)
auth_header = {"Authorization": f"Bearer {jwt}"}

# Endpoint URL
url = "https://g-run-v2-gateway-yng6lklq7a-uc.a.run.app"
# Name
my_name = "Foo bar"

"""

url = "http://127.0.0.1:8080"
my_name = "Casey"

# Request 1) without header and 2) with header
# Method 1
resp = requests.get(f"{url}/hello")
print(resp.content.decode())

"""""
    # Method 2
resp = requests.get(f"{url}/hello/{my_name}")
print(resp.content.decode())
    # Method 3
resp = requests.post(
    f"{url}/hello_body", data={"my_name": my_name}
)
"""
print(resp.content.decode())