import pytest
from authlib.integrations.base_client import OAuthError
from authlib.jose.errors import InvalidClaimError

from pcapi.connectors.sso.exceptions import GoogleSignInException
from pcapi.connectors.sso.exceptions import SSOException
from pcapi.connectors.sso.google import GoogleSSOProvider
from pcapi.utils import requests


@pytest.fixture(name="google_oauth")
def google_oauth_fixture(mocker):
    """Replace the Authlib client registered on the Flask app (no call to Google)."""
    native_app_oauth = mocker.patch("pcapi.flask_app.native_app_oauth")
    return native_app_oauth.google


class ValidateTokenTest:
    def test_returns_sso_user_from_identity_token(self, google_oauth):
        google_oauth.fetch_access_token.return_value = {"access_token": "google-access-token", "id_token": "ey..."}
        google_oauth.parse_id_token.return_value = {
            "iss": "https://accounts.google.com",
            "aud": "google-client-id",
            "sub": "100428144463745704968",
            "email": "jeune@example.com",
            "email_verified": True,
            "name": "Jeune",
        }
        provider = GoogleSSOProvider(client_type="mobile")

        sso_user = provider.validate_token("google-authorization-code")

        assert sso_user.sub == "100428144463745704968"
        assert sso_user.email == "jeune@example.com"
        assert sso_user.email_verified is True
        assert sso_user.is_private_email is None
        assert sso_user.extra_data is None
        google_oauth.parse_id_token.assert_called_once_with(google_oauth.fetch_access_token.return_value, nonce=None)

    @pytest.mark.parametrize("client_type,redirect_uri", [("web", "postmessage"), ("mobile", None)])
    def test_exchanges_code_with_redirect_uri(self, google_oauth, client_type, redirect_uri):
        google_oauth.parse_id_token.return_value = {"sub": "100428144463745704968"}
        provider = GoogleSSOProvider(client_type=client_type, redirect_uri=redirect_uri)

        provider.validate_token("google-authorization-code")

        google_oauth.fetch_access_token.assert_called_once_with(
            code="google-authorization-code", redirect_uri=redirect_uri
        )

    @pytest.mark.parametrize(
        "error",
        [
            pytest.param(OAuthError(error="invalid_grant", description="Bad Request"), id="expired or used code"),
            pytest.param(requests.exceptions.ConnectionError(), id="network error"),
        ],
    )
    def test_raises_when_code_cannot_be_exchanged(self, google_oauth, error):
        google_oauth.fetch_access_token.side_effect = error
        provider = GoogleSSOProvider(client_type="mobile")

        with pytest.raises(GoogleSignInException):
            provider.validate_token("google-authorization-code")

    def test_raises_on_invalid_identity_token(self, google_oauth):
        google_oauth.parse_id_token.side_effect = InvalidClaimError("aud")
        provider = GoogleSSOProvider(client_type="mobile")

        with pytest.raises(GoogleSignInException):
            provider.validate_token("google-authorization-code")

    def test_raises_without_identity_token(self, google_oauth):
        google_oauth.parse_id_token.return_value = None
        provider = GoogleSSOProvider(client_type="mobile")

        with pytest.raises(GoogleSignInException):
            provider.validate_token("google-authorization-code")

    def test_errors_are_sso_exceptions(self, google_oauth):
        google_oauth.fetch_access_token.side_effect = OAuthError(error="invalid_grant")
        provider = GoogleSSOProvider(client_type="mobile")

        with pytest.raises(SSOException):
            provider.validate_token("google-authorization-code")


class RevokeAccessTest:
    def test_does_nothing(self, google_oauth):
        provider = GoogleSSOProvider(client_type="mobile")

        assert provider.revoke_access() is None
        assert not google_oauth.method_calls
