from create_jwt_from_sa import generate_jwt

sa_keyfile = "envelopes-370717-b88e05596a2e.json"
sa_email = "envelopes@envelopes-370717.iam.gserviceaccount.com"
expire = 3000  # you can set some integer
aud = "https://e-app-rmgdphogrq-uc.a.run.app"

jwt = generate_jwt(sa_keyfile, sa_email, expire, aud)

# URL for Flask application on Cloud Run
#APPLICATION_URL = "https://g-run-v2-yng6lklq7a-uc.a.run.app"
# URL for Cloud Endpoint on Cloud Run
#ENDPOINT_HOST = "g-run-v2-gateway-yng6lklq7a-uc.a.run.app"
## Also need to have parameters below
#$AUD_URL