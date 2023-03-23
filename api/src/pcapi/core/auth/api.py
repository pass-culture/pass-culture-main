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
from sqlalchemy.orm import joinedload

from pcapi import settings
from pcapi.core.permissions import models as perm_models
from pcapi.core.users import models as users_models
from pcapi.core.users import repository as users_repository
from pcapi.core.users.utils import decode_jwt_token
from pcapi.core.users.utils import encode_jwt_payload
from pcapi.models import db
from pcapi.utils import requests


TOKEN_URI = "https://accounts.google.com/o/oauth2/token"

BACKOFFICE_SERVICE_ACCOUNT_SCOPES = ("https://www.googleapis.com/auth/admin.directory.group.readonly",)

BACKOFFICE_ROLE_NAME_RE = re.compile(
    (r"^backoffice-((?P<env>(testing|staging|production|integration))-)?(?P<role>.+)$")
)
BEARER_RE = re.compile(r"^Bearer (?P<token>.+)$")


class BadGoogleIdToken(Exception):
    pass


class BadPCToken(Exception):
    pass


class NotAPassCultureTeamAccountError(Exception):
    pass


def get_google_token_id_info(google_token_id: str) -> dict:
    response = requests.get(
        "https://oauth2.googleapis.com/tokeninfo",
        params={"id_token": google_token_id},
    )
    if response.status_code != 200:
        raise BadGoogleIdToken

    return response.json()


def get_user_from_google_id(token: str) -> users_models.User | None:
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


def extract_roles_from_google_workspace_groups(api_response: dict) -> set[str]:
    roles = set()
    for group in api_response.get("groups", []):
        if match := BACKOFFICE_ROLE_NAME_RE.match(group.get("name")):
            # add role if either:
            #   1. no env defined inside role name (eg. backoffice-admin
            #      instead of backoffice-staging-admin) or
            #   2. defined env does not match the current env
            env = match.group("env")
            if env and env.lower() != settings.ENV:
                continue

            roles.add(match.group("role"))
    return roles


def get_permissions_from_roles(roles: set[str]) -> list[perm_models.Permission]:
    # single db request to check roles and get permissions
    db_roles = (
        perm_models.Role.query.filter(perm_models.Role.name.in_(roles))
        .options(joinedload(perm_models.Role.permissions))
        .all()
    )

    # Create missing roles, without permission linked,
    # so that new groups extracted from Google Workspace are automatically created
    if len(db_roles) < len(roles):
        missing_roles = set(roles) - {db_role.name for db_role in db_roles}
        if missing_roles:
            for name in missing_roles:
                db.session.add(perm_models.Role(name=name))
            db.session.commit()

    permissions = set()
    for db_role in db_roles:
        permissions.update(db_role.permissions)
    return list(permissions)


def generate_token(
    user: users_models.User,
    permissions: typing.Iterable[perm_models.Permission],
    expiration: datetime | None = None,
) -> str:
    payload = {"email": user.email, "perms": [p.name for p in permissions]}
    expiration_date = datetime.utcnow() + timedelta(days=1) if expiration is None else expiration
    encoded_jwt = encode_jwt_payload(payload, expiration_date)
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

    if (user := users_models.User.query.filter_by(email=payload["email"]).one_or_none()) is None:
        raise NotAPassCultureTeamAccountError

    permissions = payload["perms"]

    return user, permissions
