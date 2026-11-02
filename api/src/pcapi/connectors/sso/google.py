import logging
from typing import Literal

from authlib.common.errors import AuthlibBaseError

from pcapi.connectors.sso.base import SSOProvider
from pcapi.connectors.sso.exceptions import GoogleSignInException
from pcapi.connectors.sso.models import SSOUser
from pcapi.utils import requests


logger = logging.getLogger(__name__)


class GoogleSSOProvider(SSOProvider):
    """Google Sign-In, relying on the Authlib client registered on the Flask app (`native_app_oauth.google`).

    The client id and secret are read by Authlib from `settings.GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET`.
    """

    # TODO: replace native_app_oauth with proper oauth, decoupled from Flask
    def __init__(
        self,
        client_type: Literal["web", "mobile"],
        redirect_uri: str | None = None,
    ):
        """
        :param redirect_uri: "postmessage" for the web app (popup flow), None for the mobile apps.
        """
        super().__init__(client_type=client_type)

        self.redirect_uri = redirect_uri

    def validate_token(self, authorization_code: str) -> SSOUser:
        """Exchange the code with Google and load the user from the OpenID Connect identity token.

        Authlib verifies the identity token (signature, audience, issuer, expiration).

        :raise GoogleSignInException: on OAuth errors (e.g. expired or already used code), network errors or
            invalid identity tokens.
        """
        from pcapi.flask_app import native_app_oauth  # avoid circular import

        try:
            token = native_app_oauth.google.fetch_access_token(
                code=authorization_code,
                redirect_uri=self.redirect_uri,
            )
            id_token = native_app_oauth.google.parse_id_token(token, nonce=None)
            return SSOUser.model_validate(id_token)
        # ValueError includes pydantic ValidationError (e.g. no identity token in the response)
        except (AuthlibBaseError, requests.exceptions.RequestException, ValueError) as e:
            logger.error(
                "Google sign in failed",
                extra={"error": str(e), "error_type": type(e).__name__},
            )
            raise GoogleSignInException("Could not validate Google authorization code") from e

    def revoke_access(self) -> None:
        """
        Revocation not yet implemented, just bypassed for now.
        """
        return
