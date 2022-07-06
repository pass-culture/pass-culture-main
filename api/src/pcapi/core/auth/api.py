from datetime import datetime
from datetime import timedelta
import re
import typing

import google.auth
from google.auth import credentials as auth_credentials
from google.auth import iam
from google.auth.transport import requests as auth_requests
from google.oauth2 import service_account
import googleapiclient.discovery

from pcapi import settings
from pcapi.core.permissions import models as perm_models
from pcapi.core.users import models as users_models
from pcapi.core.users import repository as users_repository
from pcapi.core.users.utils import decode_jwt_token
from pcapi.core.users.utils import encode_jwt_payload
from pcapi.utils import requests


TOKEN_URI = "https://accounts.google.com/o/oauth2/token"

BACKOFFICE_SERVICE_ACCOUNT_SCOPES = ("https://www.googleapis.com/auth/admin.directory.group.readonly",)

BACKOFFICE_ROLE_NAME_RE = re.compile(r"^backoffice-(?P<role>.+)$")
BEARER_RE = re.compile(r"^Bearer (?P<token>.+)$")


class BadGoogleIdToken(Exception):
    pass


class BadPCToken(Exception):
    pass


class NotAPassCultureTeamAccountError(Exception):
    pass


class ExpiredTokenError(Exception):
    pass


def get_google_token_id_info(google_token_id: str) -> dict:
    response = requests.get(
        "https://oauth2.googleapis.com/tokeninfo",
        params={"id_token": google_token_id},
    )
    if response.status_code != 200:
        raise BadGoogleIdToken

    return response.json()


def get_user_from_google_id(token: str) -> typing.Optional[users_models.User]:
    google_user = get_google_token_id_info(token)
    google_email = google_user.get("email", "")
    db_user = users_repository.find_user_by_email(google_email)
    return db_user


def delegate_credentials(
    credentials: auth_credentials.Credentials, subject: str, scopes: tuple[str]
) -> service_account.Credentials:
    request = auth_requests.Request()

    credentials.refresh(request)

    signer = iam.Signer(request, credentials, credentials.service_account_email)

    updated_credentials = service_account.Credentials(
        signer, credentials.service_account_email, TOKEN_URI, scopes=scopes, subject=subject
    )

    return updated_credentials


def get_groups_from_google_workspace(email: str) -> dict:
    credentials, _ = google.auth.default()
    delegated_credentials = delegate_credentials(
        credentials, settings.BACKOFFICE_USER_EMAIL, BACKOFFICE_SERVICE_ACCOUNT_SCOPES
    )
    directory_service = googleapiclient.discovery.build("admin", "directory_v1", credentials=delegated_credentials)
    response = directory_service.groups().list(userKey=email).execute()
    return response


def extract_roles_from_google_workspace_groups(api_response: dict) -> list[str]:
    roles = []
    for group in api_response.get("groups", []):
        if match := BACKOFFICE_ROLE_NAME_RE.match(group.get("name")):
            roles.append(match.group("role"))
    return roles


def get_permissions_from_roles(roles: typing.Iterable[str]) -> list[perm_models.Permission]:
    permissions = perm_models.Permission.query.filter(
        perm_models.Permission.roles.any(perm_models.Role.name.in_(roles))
    )
    return permissions.all()


def generate_token(user: users_models.User, permissions: typing.Iterable[perm_models.Permission]) -> str:
    payload = {"email": user.email, "perms": [p.name for p in permissions]}
    expiratione_date = datetime.utcnow() + timedelta(days=1)
    encoded_jwt = encode_jwt_payload(payload, expiratione_date)
    return encoded_jwt


def authenticate_with_permissions(google_token_id: str) -> str:
    if (user := get_user_from_google_id(google_token_id)) is None or not user.email.endswith("@passculture.app"):
        raise NotAPassCultureTeamAccountError

    groups = get_groups_from_google_workspace(user.email)
    backoffice_roles = extract_roles_from_google_workspace_groups(groups)
    permissions = get_permissions_from_roles(backoffice_roles)
    token = generate_token(user, permissions)
    return token


def authenticate_from_bearer(bearer: str) -> tuple[users_models.User, list[str]]:
    match = BEARER_RE.match(bearer)
    if match is None:
        raise BadPCToken

    token = match.group("token")
    payload = decode_jwt_token(token)
    if (expiration := payload.get("exp")) is not None and datetime.fromtimestamp(expiration) < datetime.utcnow():
        raise ExpiredTokenError

    if (user := users_models.User.query.filter_by(email=payload["email"]).one_or_none()) is None:
        raise NotAPassCultureTeamAccountError

    permissions = payload["perms"]

    return user, permissions
