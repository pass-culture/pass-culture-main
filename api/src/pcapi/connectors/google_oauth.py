from flask import request
import pydantic.v1 as pydantic_v1

from pcapi.flask_app import oauth
from pcapi.routes.serialization import ConfiguredBaseModel


class GoogleUser(ConfiguredBaseModel):
    sub: str
    email: str
    email_verified: bool


def get_google_user(authorization_code: str) -> GoogleUser:
    # postmessage is needed when the app uses a popup to fetch the authorization code
    # see https://stackoverflow.com/questions/71968377
    redirect_uri = "postmessage" if request.headers.get("platform") == "web" else None
    token = oauth.google.fetch_access_token(code=authorization_code, redirect_uri=redirect_uri)
    google_user = pydantic_v1.parse_obj_as(GoogleUser, oauth.google.parse_id_token(token))
    return google_user
