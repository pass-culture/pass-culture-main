import json
import logging
import time
import typing
import uuid

import jwt
from jwt import PyJWKClient
from urllib3 import exceptions as urllib3_exceptions

from pcapi import settings
from pcapi.core.users import schemas as users_schemas
from pcapi.utils import crypto
from pcapi.utils import requests


logger = logging.getLogger(__name__)


class AppleSignInException(Exception):
    pass


def get_apple_user(authorization_code: str, is_web: bool) -> tuple[users_schemas.SSOUser, str | None]:
    client_id = settings.APPLE_WEB_CLIENT_ID if is_web else settings.APPLE_MOBILE_CLIENT_ID
    client_secret = _generate_client_secret(client_id)

    try:
        token_response = _fetch_token_response(client_id, client_secret, authorization_code)
        id_token = token_response["id_token"]
    except Exception as e:
        raise AppleSignInException("Could not fetch identity token from Apple") from e

    refresh_token = token_response.get("refresh_token")

    jwks_client = PyJWKClient(settings.APPLE_KEYS_URL)

    try:
        signing_key = jwks_client.get_signing_key_from_jwt(id_token)
    except (jwt.PyJWTError, Exception) as e:
        logger.error("Apple JWKS fetch failed", extra={"error": str(e)})
        raise AppleSignInException("Failed to verify Apple signing keys") from e

    try:
        token_payload = jwt.decode(
            id_token,
            signing_key.key,
            algorithms=["RS256"],
            audience=client_id,
            issuer=settings.APPLE_ISSUER_URL,
            options=jwt.types.Options(verify_signature=True),
        )
    except jwt.PyJWTError as e:
        logger.error("Apple identity token validation failed", extra={"error": str(e), "error_type": type(e).__name__})
        raise AppleSignInException("Invalid identity token") from e

    return _parse_identity_token(token_payload), refresh_token


def build_refresh_token_payload(refresh_token: str, is_web: bool) -> str:
    # Store the client_id: Apple ties the refresh token to it and it cannot be recomputed later.
    client_id = settings.APPLE_WEB_CLIENT_ID if is_web else settings.APPLE_MOBILE_CLIENT_ID
    return crypto.encrypt(json.dumps({"refresh_token": refresh_token, "client_id": client_id}))


def decrypt_refresh_token_payload(refresh_token_payload: str) -> tuple[str, str]:
    payload = json.loads(crypto.decrypt(refresh_token_payload))
    return payload["refresh_token"], payload["client_id"]


def revoke_refresh_token(refresh_token: str, client_id: str) -> None:
    # https://developer.apple.com/documentation/sign_in_with_apple/revoke_tokens
    client_secret = _generate_client_secret(client_id)
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "token": refresh_token,
        "token_type_hint": "refresh_token",
    }
    # Short timeout: this may run inside the anonymization transaction, holding row locks.
    response = requests.post(settings.APPLE_REVOKE_ENDPOINT, data=data, timeout=3)
    response.raise_for_status()


def _generate_client_secret(client_id: str) -> str:
    # Doc on how to generate a client secret: https://developer.apple.com/documentation/AccountOrganizationalDataSharing/creating-a-client-secret
    now = int(time.time())
    payload = {
        "iss": settings.APPLE_TEAM_ID,
        "iat": now,
        "exp": now + 180,  # short-lived: used immediately for a single request
        "aud": settings.APPLE_ISSUER_URL,
        "sub": client_id,
        "jti": str(uuid.uuid4()),
    }
    headers = {"alg": "ES256", "kid": settings.APPLE_KEY_ID}
    return jwt.encode(payload, settings.APPLE_PRIVATE_KEY, headers=headers)


def _fetch_token_response(client_id: str, client_secret: str, authorization_code: str) -> dict[str, typing.Any]:
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": authorization_code,
        "grant_type": "authorization_code",
    }

    try:
        response = requests.post(settings.APPLE_TOKEN_ENDPOINT, data=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code
        logger.error("Error fetching Apple token", extra={"response": str(e), "status_code": status})
        raise

    except ValueError as e:
        # requests' JSONDecodeError subclasses both ValueError and RequestException: keep this
        # clause first so a malformed body is not logged as a network error.
        logger.error("Malformed response from Apple Token API", extra={"error": str(e)})
        raise

    except (urllib3_exceptions.HTTPError, requests.exceptions.RequestException) as e:
        logger.error("Network error reaching Apple", extra={"error": str(e)})
        raise


def _parse_identity_token(payload: dict[str, typing.Any]) -> users_schemas.SSOUser:
    # Doc on id_token content: https://developer.apple.com/documentation/signinwithapplejs/authorizationi/id_token
    is_private_email = payload.get("is_private_email")
    if isinstance(is_private_email, str):
        is_private_email = is_private_email.lower() == "true"

    email_verified = payload.get("email_verified")
    if isinstance(email_verified, str):
        email_verified = email_verified.lower() == "true"

    return users_schemas.SSOUser(
        sub=payload["sub"],
        email=payload.get("email"),
        email_verified=email_verified,
        is_private_email=is_private_email,
    )
