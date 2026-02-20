from flask import request

from pcapi.core.users import schemas as users_schemas
from pcapi.flask_app import native_app_oauth


def get_google_user(authorization_code: str) -> users_schemas.SSOUser:
    # postmessage is needed when the app uses a popup to fetch the authorization code
    # see https://stackoverflow.com/questions/71968377
    redirect_uri = "postmessage" if request.headers.get("platform") == "web" else None
    token = native_app_oauth.google.fetch_access_token(code=authorization_code, redirect_uri=redirect_uri)
    google_user = users_schemas.SSOUser.model_validate(native_app_oauth.google.parse_id_token(token, nonce=None))
    return google_user
