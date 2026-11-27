import logging
import re
import typing

import google.auth
import googleapiclient.discovery
from google.auth import credentials as auth_credentials
from google.auth import iam
from google.auth.transport import requests as auth_requests
from google.oauth2 import id_token
from google.oauth2 import service_account

from pcapi import settings
from pcapi.connectors.sso import SSOProviderFactory
from pcapi.connectors.sso import SSOProviderName
from pcapi.connectors.sso import SSOUser
from pcapi.core.auth import exceptions
from pcapi.core.auth import repository


if typing.TYPE_CHECKING:
    from pcapi.core.users.models import User


TOKEN_URI = "https://accounts.google.com/o/oauth2/token"

BACKOFFICE_SERVICE_ACCOUNT_SCOPES = ("https://www.googleapis.com/auth/admin.directory.group.readonly",)

BACKOFFICE_ROLE_NAME_RE = re.compile(
    r"^backoffice-((?P<env>(development|testing|staging|production|integration))-)(?P<role>.+)$"
)

logger = logging.getLogger(__name__)


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


def get_sso_user_from_auth_token(authorization_code: str, provider: SSOProviderName, is_web: bool) -> SSOUser:
    sso_provider = SSOProviderFactory.create(provider, is_web)
    user = sso_provider.validate_token(authorization_code)

    return user


def attach_sso_to_user(user: "User", sso_user: SSOUser, provider: str) -> "User":
    try:
        sso_provider = SSOProviderName(provider)
    except ValueError as e:
        raise exceptions.SSOUnsupportedProvider from e

    if user.has_anonymized_role or user.account_state.is_deleted:
        raise exceptions.SSOAccountNotActive

    if not (user.isEmailValidated and sso_user.email_verified):
        raise exceptions.SSOUnverifiedEmail

    if user.get_sso(sso_provider) is not None:
        raise exceptions.SSOAlreadyAttached

    if repository.get_single_sign_on_from_provider(sso_provider, sso_user.sub) is not None:
        raise exceptions.SSOAttachedToAnotherAccount

    repository.create_single_sign_on(
        user,
        sso_provider,
        sso_user.sub,
        sso_user.extra_data,
    )

    return user


def remove_sso_from_user(user: "User", sso_user_id: int) -> None:
    if not (sso := repository.get_single_sign_on_from_id(sso_user_id)):
        raise exceptions.SSOUserNotFound

    if not (attached_sso := user.get_sso(sso.ssoProvider)):
        raise exceptions.SSOAttachedToAnotherAccount

    if sso.id != attached_sso.id:
        raise exceptions.SSOAttachedToAnotherAccount

    try:
        provider = SSOProviderName(sso.ssoProvider)
    except ValueError as e:
        raise exceptions.SSOUnsupportedProvider from e

    revoke_sso_access(user, provider)


def revoke_sso_access(
    user: "User",
    provider: SSOProviderName | None = None,
) -> None:
    """
    Revoke the single sign-on connections from a user to an external provider (all providers if `provider` is None).

    Delete also the linked SSOUser from our database.
    """

    for sso in user.single_sign_ons:
        if provider is not None and sso.ssoProvider != provider:
            continue

        if sso.ssoProvider == SSOProviderName.APPLE:
            # Trying to revoke Apple SSO from pc-api.
            # Revocation on Apple could fail, due to bad refresh_token, but user
            # can do it on their side (follow doc linked in revoke_apple_user function)
            extra_data: dict[str, str] = sso.ssoExtraData or {}

            for client_type, token in extra_data.items():
                is_web_client = client_type == "web"

                try:
                    sso_provider = SSOProviderFactory.create(SSOProviderName.APPLE, is_web_client)
                    sso_provider.revoke_access(token)

                except Exception as exc:
                    logger.warning(
                        "Could not revoke Apple SSO",
                        extra={"user_id": user.id, "exc": str(exc)},
                    )

        repository.delete_sso_user(sso.id)
