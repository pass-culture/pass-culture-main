import logging
import time
import typing
from functools import lru_cache
from typing import Literal
from uuid import uuid4

import jwt
from jwt import PyJWKClient
from jwt import types
from pydantic import ValidationError
from urllib3 import exceptions as urllib3_exceptions

from pcapi.connectors.sso.base import SSOProvider
from pcapi.connectors.sso.exceptions import AppleRevokeException
from pcapi.connectors.sso.exceptions import AppleSignInException
from pcapi.connectors.sso.models import AppleSignInAuthenticationResponse
from pcapi.connectors.sso.models import SSOUser
from pcapi.utils import requests


AUTH_ENDPOINT = "https://appleid.apple.com/auth/token"
REVOKE_ENDPOINT = "https://appleid.apple.com/auth/revoke"
KEYS_URL = "https://appleid.apple.com/auth/keys"
ISSUER_URL = "https://appleid.apple.com"

logger = logging.getLogger(__name__)


class AppleSSOProvider(SSOProvider):
    """Sign in with Apple, implemented directly on the Apple REST API.

    https://developer.apple.com/documentation/signinwithapplerestapi

    Apple does not use a static client secret: each call signs a short-lived JWT with our private key
    (see `__generate_client_secret`).
    """

    def __init__(
        self,
        client_id: str,
        team_id: str,
        key_id: str,
        private_key: str,
        token_exp: int,
        client_type: Literal["web", "mobile"],
    ):
        """
        :param client_id: Services ID for the web app, App ID (bundle id) for the mobile apps.
        :param team_id: Apple developer team id, issuer of the client secret.
        :param key_id: id of the "Sign in with Apple" private key.
        :param private_key: ES256 private key (PEM) used to sign the client secret.
        :param token_exp: lifetime of the generated client secret, in seconds.
        """
        super().__init__(client_type=client_type)

        self.client_id = client_id
        self.team_id = team_id
        self.key_id = key_id
        self.private_key = private_key
        self.token_exp = token_exp

    def validate_token(self, authorization_code: str) -> SSOUser:
        """Exchange the code with Apple, verify the identity token and build the user.

        The refresh token returned by Apple is kept in `SSOUser.extra_data` (keyed by client type), because it is
        the only way to revoke the access later (see `revoke_access`).

        :raise AppleSignInException: on network errors, unexpected responses or invalid identity tokens.
        """
        try:
            payload = {
                "client_id": self.client_id,
                "client_secret": self.__generate_client_secret(),
                "code": authorization_code,
                "grant_type": "authorization_code",
            }
            response = self.__fetch_response(AUTH_ENDPOINT, payload)
        except Exception as e:
            raise AppleSignInException("Could not fetch identity token from Apple") from e

        try:
            if isinstance(response, str):
                raise ValidationError

            auth_response = AppleSignInAuthenticationResponse(**response)
        except ValidationError as e:
            raise AppleSignInException("Unexpected response format from Apple Token API") from e

        token_payload = self.__decrypt_identity_token(auth_response.id_token)

        return self.__generate_sso_user(token_payload, auth_response)

    def revoke_access(self, refresh_token: str) -> None:
        """
        Revoke Apple SignIn User on Apple-side, with the user's Apple refresh token.

        Refresh token have no expiry date, so we can just use the one from account creation

        Users can remove their SSO from their Apple Account: https://support.apple.com/en-us/102571

        Revoke documentation: https://developer.apple.com/documentation/signinwithapplerestapi/revoke-tokens
        """
        try:
            payload = {
                "client_id": self.client_id,
                "client_secret": self.__generate_client_secret(),
                "token": refresh_token,
                "token_type_hint": "refresh_token",
            }
            self.__fetch_response(REVOKE_ENDPOINT, payload, should_expect_json=False)
            logger.info("Account successfully revoked from Apple services")

        except Exception as e:
            raise AppleRevokeException("Could not revoke user from Apple") from e

    # Requests
    def __fetch_response(self, url: str, payload: dict, should_expect_json: bool = True) -> str | dict:
        """POST a form to an Apple endpoint, log failures and re-raise them (wrapped by the callers).

        :param should_expect_json: False for endpoints returning an empty body (revocation).
        """
        try:
            response = requests.post(url, data=payload)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            assert e.response is not None
            status = e.response.status_code
            logger.error("Error fetching Apple token", extra={"response": str(e), "status_code": status})
            raise

        except (urllib3_exceptions.HTTPError, requests.exceptions.RequestException) as e:
            logger.error("Network error reaching Apple", extra={"error": str(e)})
            raise

        except (KeyError, ValueError) as e:
            logger.error("Malformed response from Apple Token API", extra={"error": str(e)})
            raise

        if not should_expect_json:
            return response.text

        try:
            json_payload = response.json()
        except requests.exceptions.JSONDecodeError as e:
            logger.error("Malformed response from Apple Token API", extra={"error": str(e)})
            raise

        return json_payload

    # Apple Related functions
    @classmethod
    @lru_cache(maxsize=1)
    def __get_jwks_client(self, url: str) -> PyJWKClient:
        """Client fetching the Apple public keys, shared between instances so that the keys stay cached."""
        return PyJWKClient(url)

    def __generate_client_secret(self) -> str:
        """
        Apple documentation on how to generate a client secret:
        https://developer.apple.com/documentation/AccountOrganizationalDataSharing/creating-a-client-secret
        """
        now = int(time.time())
        payload = {
            "iss": self.team_id,
            "iat": now,
            "jti": str(uuid4()),
            "exp": now + self.token_exp,
            "aud": ISSUER_URL,
            "sub": self.client_id,
        }
        headers = {"alg": "ES256", "kid": self.key_id}

        return jwt.encode(payload, self.private_key, headers=headers)

    def __decrypt_identity_token(self, token: str) -> dict[str, typing.Any]:
        """Verify the identity token against the Apple public keys and return its claims.

        Checks the signature (RS256), the audience (our client id), the issuer and the expiration.

        :raise AppleSignInException: if the keys cannot be fetched or the token is invalid.
        """
        jwks_client = self.__get_jwks_client(KEYS_URL)

        try:
            signing_key = jwks_client.get_signing_key_from_jwt(token)
        except (jwt.PyJWTError, Exception) as e:
            logger.error("Apple JWKS fetch failed", extra={"error": str(e)})
            raise AppleSignInException("Failed to verify Apple signing keys") from e

        try:
            token_payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=self.client_id,
                issuer=ISSUER_URL,
                options=types.Options(verify_signature=True),
            )
        except jwt.PyJWTError as e:
            logger.error(
                "Apple identity token validation failed",
                extra={
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
            )
            raise AppleSignInException("Invalid identity token") from e

        return token_payload

    def __generate_sso_user(
        self,
        id_token_payload: dict[str, typing.Any],
        token_response: AppleSignInAuthenticationResponse,
    ) -> SSOUser:
        """
        Retrieve identity from Apple ID Token.

        Doc on id_token content:
            https://developer.apple.com/documentation/signinwithapplejs/authorizationi/id_token
        """
        is_private_email = id_token_payload.get("is_private_email")
        if isinstance(is_private_email, str):
            is_private_email = is_private_email.lower() == "true"

        email_verified = id_token_payload.get("email_verified")
        if isinstance(email_verified, str):
            email_verified = email_verified.lower() == "true"

        return SSOUser(
            sub=id_token_payload.get("sub", ""),
            email=id_token_payload.get("email"),
            email_verified=email_verified,
            is_private_email=is_private_email,
            extra_data={
                self.client_type: token_response.refresh_token,
            },
        )
