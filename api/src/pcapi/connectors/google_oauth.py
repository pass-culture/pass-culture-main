import pydantic
from flask import request

from pcapi.flask_app import native_app_oauth


class GoogleUser(pydantic.BaseModel):
    sub: str
    email: str
    email_verified: bool


def get_google_user(authorization_code: str) -> GoogleUser:
    # postmessage is needed when the app uses a popup to fetch the authorization code
    # see https://stackoverflow.com/questions/71968377
    redirect_uri = "postmessage" if request.headers.get("platform") == "web" else None
    token = native_app_oauth.google.fetch_access_token(code=authorization_code, redirect_uri=redirect_uri)
    google_user = GoogleUser.model_validate(native_app_oauth.google.parse_id_token(token, nonce=None))
    return google_user
