import logging
import time
import typing
from uuid import uuid4

import jwt
from jwt import PyJWKClient
from jwt import types
from pydantic import BaseModel
from pydantic.errors import ValidationError
from urllib3 import exceptions as urllib3_exceptions

from pcapi import settings
from pcapi.core.users import schemas as users_schemas
from pcapi.utils import requests


logger = logging.getLogger(__name__)


class AppleSignInAuthenticationResponse(BaseModel):
    id_token: str
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str


class AppleSignInException(Exception):
    pass


def get_apple_user(authorization_code: str, is_web: bool) -> users_schemas.SSOUser:
    client_id = settings.APPLE_WEB_CLIENT_ID if is_web else settings.APPLE_MOBILE_CLIENT_ID
    client_secret = _generate_client_secret(client_id)

    try:
        apple_payload = _fetch_identity_response(client_id, client_secret, authorization_code)
    except Exception as e:
        raise AppleSignInException("Could not fetch identity token from Apple") from e

    jwks_client = PyJWKClient(settings.APPLE_KEYS_URL)

    try:
        signing_key = jwks_client.get_signing_key_from_jwt(apple_payload.id_token)
    except (jwt.PyJWTError, Exception) as e:
        logger.error("Apple JWKS fetch failed", extra={"error": str(e)})
        raise AppleSignInException("Failed to verify Apple signing keys") from e

    try:
        token_payload = jwt.decode(
            apple_payload.id_token,
            signing_key.key,
            algorithms=["RS256"],
            audience=client_id,
            issuer=settings.APPLE_ISSUER_URL,
            options=types.Options(verify_signature=True),
        )
    except jwt.PyJWTError as e:
        logger.error("Apple identity token validation failed", extra={"error": str(e), "error_type": type(e).__name__})
        raise AppleSignInException("Invalid identity token") from e

    return _parse_identity_token(token_payload)


def _generate_client_secret(client_id: str) -> str:
    # Doc on how to generate a client secret: https://developer.apple.com/documentation/AccountOrganizationalDataSharing/creating-a-client-secret
    now = int(time.time())
    payload = {
        "iss": settings.APPLE_TEAM_ID,
        "iat": now,
        "jti": uuid4(),
        "exp": now + int(settings.APPLE_TOKEN_EXPIRATION),
        "aud": settings.APPLE_ISSUER_URL,
        "sub": client_id,
    }
    headers = {"alg": "ES256", "kid": settings.APPLE_KEY_ID}
    return jwt.encode(payload, settings.APPLE_PRIVATE_KEY, headers=headers)


def _fetch_identity_response(
    client_id: str,
    client_secret: str,
    authorization_code: str,
) -> AppleSignInAuthenticationResponse:
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": authorization_code,
        "grant_type": "authorization_code",
    }

    try:
        response = requests.post(settings.APPLE_TOKEN_ENDPOINT, data=payload)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code
        logger.error("Error fetching Apple token", extra={"response": str(e), "status_code": status})
        raise

    except (urllib3_exceptions.HTTPError, requests.exceptions.RequestException) as e:
        logger.error("Network error reaching Apple", extra={"error": str(e)})
        raise

    except (KeyError, ValueError) as e:
        logger.error("Malformed response from Apple Token API", extra={"error": str(e)})
        raise

    try:
        json_payload = response.json()
        typed_response = AppleSignInAuthenticationResponse(**json_payload)
    except requests.exceptions.JSONDecodeError as e:
        logger.error("Malformed response from Apple Token API", extra={"error": str(e)})
        raise
    except ValidationError as e:
        logger.error("Unexpected response format from Apple Token API", extra={"error": str(e)})
        raise

    return typed_response


def _parse_identity_token(
    payload: dict[str, typing.Any],
    token_response: AppleSignInAuthenticationResponse,
) -> users_schemas.SSOUser:
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
        extra_data={"refresh_token": token_response.refresh_token},
    )
