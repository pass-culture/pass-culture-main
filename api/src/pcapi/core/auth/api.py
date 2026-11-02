import re

import google.auth
import googleapiclient.discovery
from google.auth import credentials as auth_credentials
from google.auth import iam
from google.auth.transport import requests as auth_requests
from google.oauth2 import id_token
from google.oauth2 import service_account

from pcapi import settings
from pcapi.connectors.sso import SSOProviderFactory
from pcapi.connectors.sso import SSOUser
from pcapi.core.auth import exceptions
from pcapi.core.auth import repository
from pcapi.core.users import repository as users_repo
from pcapi.core.users.models import User


TOKEN_URI = "https://accounts.google.com/o/oauth2/token"

BACKOFFICE_SERVICE_ACCOUNT_SCOPES = ("https://www.googleapis.com/auth/admin.directory.group.readonly",)

BACKOFFICE_ROLE_NAME_RE = re.compile(
    r"^backoffice-((?P<env>(development|testing|staging|production|integration))-)(?P<role>.+)$"
)


def delegate_credentials(
    credentials: auth_credentials.Credentials, subject: str, scopes: tuple[str]
) -> service_account.Credentials:
    request = auth_requests.Request()

    credentials.refresh(request)

    signer = iam.Signer(request, credentials, credentials.service_account_email)  # type: ignore[attr-defined]

    updated_credentials = service_account.Credentials(
        signer,
        credentials.service_account_email,  # type: ignore[attr-defined]
        TOKEN_URI,
        scopes=scopes,
        subject=subject,
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


def get_sso_user_from_auth_token(authorization_code: str, provider: str, is_web: bool) -> SSOUser:
    sso_provider = SSOProviderFactory.create(provider, is_web)
    user = sso_provider.validate_token(authorization_code)

    return user


def attach_sso_to_user(user: User, sso_user: SSOUser, provider: str) -> User:
    # raise if the account is not active (suspended or anonymized)
    if user.has_anonymized_role or user.is_soft_deleted():
        raise exceptions.SSOAccountNotActive

    # raise if email from user or from sso is not verified
    if user.isEmailValidated is False or not sso_user.email_verified:
        raise exceptions.SSOUnverifiedEmail

    # raise if an account has already an SSO from the same provider attached
    if user.get_sso(provider) is not None:
        raise exceptions.SSOAlreadyAttached

    # raise if the sso account is already attached to another account
    if repository.get_sso_user_by_provider_and_id(provider, sso_user.sub) is not None:
        raise exceptions.SSOAttachedToAnotherAccount

    users_repo.create_single_sign_on(
        user,
        provider,
        sso_user.sub,
        sso_user.extra_data,
    )

    return user
