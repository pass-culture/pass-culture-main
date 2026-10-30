import time
from unittest.mock import MagicMock

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric import rsa

from pcapi.connectors.sso import apple
from pcapi.connectors.sso.apple import AppleSSOProvider
from pcapi.connectors.sso.exceptions import AppleSignInException
from pcapi.connectors.sso.exceptions import SSOException
from pcapi.utils import requests


CLIENT_ID = "app.passculture.test"
TEAM_ID = "TEAM123"
KEY_ID = "KEY123"


@pytest.fixture(name="client_secret_key", scope="module")
def client_secret_key_fixture():
    """Our "Sign in with Apple" private key, used to sign the client secret (ES256)."""
    return ec.generate_private_key(ec.SECP256R1())


@pytest.fixture(name="apple_signing_key", scope="module")
def apple_signing_key_fixture():
    """Apple private key, used to sign the identity tokens (RS256)."""
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


@pytest.fixture(name="provider")
def provider_fixture(client_secret_key):
    private_key = client_secret_key.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
    ).decode()
    return AppleSSOProvider(
        client_id=CLIENT_ID,
        team_id=TEAM_ID,
        key_id=KEY_ID,
        private_key=private_key,
        token_exp=180,
        client_type="mobile",
    )


@pytest.fixture(name="apple_public_keys")
def apple_public_keys_fixture(mocker, apple_signing_key):
    """Replace the call to the Apple JWKS endpoint by the public key matching `apple_signing_key`."""
    return mocker.patch(
        "jwt.PyJWKClient.get_signing_key_from_jwt",
        return_value=MagicMock(key=apple_signing_key.public_key()),
    )


def _identity_token(signing_key, **claims):
    now = int(time.time())
    payload = {
        "iss": apple.ISSUER_URL,
        "aud": CLIENT_ID,
        "iat": now,
        "exp": now + 600,
        "sub": "000123.apple-user-id",
        "email": "jeune@example.com",
        "email_verified": "true",
        "is_private_email": "false",
    }
    payload.update(claims)
    return jwt.encode(payload, signing_key, algorithm="RS256")


def _token_response(id_token):
    return {
        "access_token": "apple-access-token",
        "refresh_token": "apple-refresh-token",
        "expires_in": 3600,
        "token_type": "Bearer",
        "id_token": id_token,
    }


@pytest.mark.usefixtures("apple_public_keys")
class ValidateTokenTest:
    def test_returns_sso_user(self, provider, requests_mock, apple_signing_key):
        requests_mock.post(apple.AUTH_ENDPOINT, json=_token_response(_identity_token(apple_signing_key)))

        sso_user = provider.validate_token("apple-authorization-code")

        assert sso_user.sub == "000123.apple-user-id"
        assert sso_user.email == "jeune@example.com"
        # Apple sends booleans as strings
        assert sso_user.email_verified is True
        assert sso_user.is_private_email is False
        # the refresh token is kept, by client type, to be able to revoke the access later
        assert sso_user.extra_data == {"mobile": "apple-refresh-token"}

    def test_refresh_token_is_keyed_by_client_type(self, provider, requests_mock, apple_signing_key):
        provider.client_type = "web"
        requests_mock.post(apple.AUTH_ENDPOINT, json=_token_response(_identity_token(apple_signing_key)))

        sso_user = provider.validate_token("apple-authorization-code")

        assert sso_user.extra_data == {"web": "apple-refresh-token"}

    def test_accepts_boolean_claims(self, provider, requests_mock, apple_signing_key):
        id_token = _identity_token(apple_signing_key, email_verified=True, is_private_email=True)
        requests_mock.post(apple.AUTH_ENDPOINT, json=_token_response(id_token))

        sso_user = provider.validate_token("apple-authorization-code")

        assert sso_user.email_verified is True
        assert sso_user.is_private_email is True

    def test_sends_code_and_signed_client_secret(self, provider, requests_mock, apple_signing_key, client_secret_key):
        requests_mock.post(apple.AUTH_ENDPOINT, json=_token_response(_identity_token(apple_signing_key)))

        provider.validate_token("apple-authorization-code")

        form = requests_mock.last_request.text
        params = dict(param.split("=", 1) for param in form.split("&"))
        assert params["client_id"] == CLIENT_ID
        assert params["code"] == "apple-authorization-code"
        assert params["grant_type"] == "authorization_code"

        client_secret = params["client_secret"]
        assert jwt.get_unverified_header(client_secret)["kid"] == KEY_ID
        claims = jwt.decode(
            client_secret, client_secret_key.public_key(), algorithms=["ES256"], audience=apple.ISSUER_URL
        )
        assert claims["iss"] == TEAM_ID
        assert claims["sub"] == CLIENT_ID
        assert claims["exp"] - claims["iat"] == 180

    def test_raises_on_http_error(self, provider, requests_mock):
        requests_mock.post(apple.AUTH_ENDPOINT, status_code=400, json={"error": "invalid_grant"})

        with pytest.raises(AppleSignInException, match="Could not fetch identity token"):
            provider.validate_token("expired-authorization-code")

    def test_raises_on_network_error(self, provider, requests_mock):
        requests_mock.post(apple.AUTH_ENDPOINT, exc=requests.exceptions.ConnectionError)

        with pytest.raises(AppleSignInException, match="Could not fetch identity token"):
            provider.validate_token("apple-authorization-code")

    def test_raises_on_invalid_json(self, provider, requests_mock):
        requests_mock.post(apple.AUTH_ENDPOINT, text="not json")

        with pytest.raises(AppleSignInException, match="Could not fetch identity token"):
            provider.validate_token("apple-authorization-code")

    def test_raises_on_unexpected_response_format(self, provider, requests_mock):
        requests_mock.post(apple.AUTH_ENDPOINT, json={"access_token": "apple-access-token"})

        with pytest.raises(AppleSignInException, match="Unexpected response format"):
            provider.validate_token("apple-authorization-code")

    @pytest.mark.parametrize(
        "claims",
        [
            pytest.param({"aud": "another.client.id"}, id="other audience"),
            pytest.param({"iss": "https://evil.example.com"}, id="other issuer"),
            pytest.param({"exp": int(time.time()) - 60}, id="expired"),
        ],
    )
    def test_raises_on_invalid_identity_token(self, provider, requests_mock, apple_signing_key, claims):
        requests_mock.post(apple.AUTH_ENDPOINT, json=_token_response(_identity_token(apple_signing_key, **claims)))

        with pytest.raises(AppleSignInException, match="Invalid identity token"):
            provider.validate_token("apple-authorization-code")

    def test_raises_on_identity_token_not_signed_by_apple(self, provider, requests_mock):
        other_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        requests_mock.post(apple.AUTH_ENDPOINT, json=_token_response(_identity_token(other_key)))

        with pytest.raises(AppleSignInException, match="Invalid identity token"):
            provider.validate_token("apple-authorization-code")

    def test_raises_when_apple_public_keys_cannot_be_fetched(
        self, provider, requests_mock, apple_signing_key, apple_public_keys
    ):
        apple_public_keys.side_effect = jwt.PyJWKClientError("The JWKS endpoint did not return a JSON object")
        requests_mock.post(apple.AUTH_ENDPOINT, json=_token_response(_identity_token(apple_signing_key)))

        with pytest.raises(AppleSignInException, match="Failed to verify Apple signing keys"):
            provider.validate_token("apple-authorization-code")

    def test_errors_are_sso_exceptions(self, provider, requests_mock):
        requests_mock.post(apple.AUTH_ENDPOINT, status_code=500)

        with pytest.raises(SSOException):
            provider.validate_token("apple-authorization-code")


class RevokeAccessTest:
    def test_revokes_refresh_token(self, provider, requests_mock):
        requests_mock.post(apple.REVOKE_ENDPOINT, status_code=200, text="")

        provider.revoke_access("apple-refresh-token")

        form = requests_mock.last_request.text
        params = dict(param.split("=", 1) for param in form.split("&"))
        assert params["client_id"] == CLIENT_ID
        assert params["token"] == "apple-refresh-token"
        assert params["token_type_hint"] == "refresh_token"
        assert params["client_secret"]

    def test_raises_on_http_error(self, provider, requests_mock):
        requests_mock.post(apple.REVOKE_ENDPOINT, status_code=400, json={"error": "invalid_client"})

        with pytest.raises(apple.AppleRevokeException, match="Could not revoke user from Apple"):
            provider.revoke_access("apple-refresh-token")
