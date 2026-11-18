from authlib.integrations.flask_client import OAuth
from flask import current_app

from pcapi import settings
from pcapi.core.users import schemas as users_schemas


native_app_oauth = OAuth(current_app)
native_app_oauth.register(
    name="google",
    client_id=settings.NATIVE_APP_GOOGLE_CLIENT_ID,
    client_secret=settings.NATIVE_APP_GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


def get_google_user(authorization_code: str, is_web: bool) -> users_schemas.SSOUser:
    # postmessage is needed when the app uses a popup to fetch the authorization code
    # see https://stackoverflow.com/questions/71968377
    redirect_uri = "postmessage" if is_web else None
    token = native_app_oauth.google.fetch_access_token(code=authorization_code, redirect_uri=redirect_uri)
    google_user = users_schemas.SSOUser.model_validate(native_app_oauth.google.parse_id_token(token, nonce=None))
    return google_user
