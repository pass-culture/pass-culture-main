import re

import google.auth
from google.auth import credentials as auth_credentials
from google.auth import iam
from google.auth.transport import requests as auth_requests
from google.oauth2 import id_token
from google.oauth2 import service_account
import googleapiclient.discovery

from pcapi import settings


TOKEN_URI = "https://accounts.google.com/o/oauth2/token"

BACKOFFICE_SERVICE_ACCOUNT_SCOPES = ("https://www.googleapis.com/auth/admin.directory.group.readonly",)

BACKOFFICE_ROLE_NAME_RE = re.compile(
    (r"^backoffice-((?P<env>(development|testing|staging|production|integration))-)(?P<role>.+)$")
)


def delegate_credentials(
    credentials: auth_credentials.Credentials, subject: str, scopes: tuple[str]
) -> service_account.Credentials:
    request = auth_requests.Request()

    credentials.refresh(request)

    signer = iam.Signer(request, credentials, credentials.service_account_email)  # type: ignore[attr-defined]

    updated_credentials = service_account.Credentials(
        signer, credentials.service_account_email, TOKEN_URI, scopes=scopes, subject=subject  # type: ignore[attr-defined]
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
            if env.lower() != settings.ENV:
                continue

            roles.add(match.group("role"))
    return roles


def get_id_token_from_google(client_id: str) -> str:
    open_id_connect_token = id_token.fetch_id_token(auth_requests.Request(), client_id)
    return open_id_connect_token
