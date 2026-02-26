from pcapi.utils import requests


class InvalidIdentityTokenError(Exception):
    pass


BACKEND_PRIVATE_KEY = ""
GOOGLE_PUBLIC_KEY = ""


def is_valid(x, y):
    pass


def decode(x):
    pass


def route(): ...


def create_refresh_token(): ...
def create_access_token(): ...
def create_token(): ...
def uuidv4(): ...


request = {}


class redis: ...


@route("/oauth/state")
def create_oauth_state_token():
    nonce = uuidv4()
    token = create_token(
        uuid=uuidv4(),
        time_to_live="30 minutes",
        data={"deviceId": request.deviceId, "nonce": nonce},
    )
    redis.save(token)
    return token.uuid


@route("/oauth/authorize")
def oauth_authorize(state, authorization_code):
    token = redis.get(state)
    if not token or token.deviceId != request.deviceId:
        return 401, "Unauthorized"

    redis.delete(state)

    user_data = fetch_identity(authorization_code)
    if not user_data or not user_data.email_verified:
        return 401, "Unauthorized"

    refresh_token = create_refresh_token(
        identity=user_data.email,
        time_to_live="30 jours",
    )
    access_token = create_access_token(
        identity=user_data.email,
        time_to_live="15 minutes",
    )
    return access_token, refresh_token


def fetch_identity(authorization_code):
    token = requests.post(
        "https://google.com/auth",
        data={
            "secret": BACKEND_PRIVATE_KEY,
            "auth_code": authorization_code,
        },
    )
    if not is_valid(token, GOOGLE_PUBLIC_KEY):
        raise InvalidIdentityTokenError

    data = decode(token)

    return {
        "google_user_id": data.sub,
        "email": data.email,
        "is_email_verified": data.is_email_verified,
    }
