"""
A sample code to create a JWT key
"""
import time
import google.auth.crypt
import google.auth.jwt


def generate_jwt(sa_keyfile, sa_email, expire, aud):
    """Create a jwt from service account"""

    current_time_int = int(time.time())

    # Build the JWT payload
    payload = {
        "iat": current_time_int,
        "exp": current_time_int + expire,  # When the token will expire
        "iss": sa_email,
        "aud": aud,  # aud: need to match to yaml file parameter
        "sub": sa_email,
        "email": sa_email,
    }

    # Use the payload and keyfile to create JWT
    signer = google.auth.crypt.RSASigner.from_service_account_file(sa_keyfile)
    # create token
    jwt = google.auth.jwt.encode(signer, payload)
    return jwt.decode()