import os
import requests


RECAPTCHA_API_URL = 'https://www.google.com/recaptcha/api/siteverify'
RECAPTCHA_SECRET = os.environ.get("RECAPTCHA_SECRET")

class ReCaptchaException(Exception):
    pass

def validate_recaptcha_token(token: str) -> bool:
    params = {
        "secret": RECAPTCHA_SECRET,
        "response": token
    }
    api_response = requests.post(RECAPTCHA_API_URL, data=params)

    if api_response.status_code != 200:
        raise ReCaptchaException(f"Couldn't reach recaptcha api: {api_response.status_code} {api_response.text}")

    json_response = api_response.json()
    return json_response["success"]
