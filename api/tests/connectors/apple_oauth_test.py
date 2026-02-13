from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
import requests_mock

from pcapi import settings
from pcapi.connectors.apple_oauth import get_apple_user


@pytest.fixture
def mock_jwks(mocker):
    mock_client = mocker.patch("jwt.PyJWKClient.get_signing_key_from_jwt")
    mock_key = MagicMock()
    mock_key.key = "fake-public-key"
    mock_client.return_value = mock_key
    return mock_client


@patch("pcapi.connectors.apple_oauth.settings.APPLE_PRIVATE_KEY")
def test_get_apple_user_success(mock_jwks, mocker):
    with requests_mock.Mocker() as mock:
        mock.post(
            settings.APPLE_TOKEN_ENDPOINT,
            status_code=200,
            json={"id_token": "mock.id.token"},
        )

        mock_client = mocker.patch("jwt.PyJWKClient.get_signing_key_from_jwt")
        mock_key = MagicMock()
        mock_key.key = "fake-public-key"
        mock_client.return_value = mock_key

        mocker.patch(
            "jwt.decode",
            return_value={
                "sub": "user_123",
                "email": "hello@example.com",
                "email_verified": "true",
            },
        )

        mocker.patch(
            "jwt.encode",
            return_value={
                "sub": "user_123",
                "email": "hello@example.com",
                "email_verified": "true",
            },
        )

        user = get_apple_user("valid_code")

    assert user.sub == "user_123"
    assert user.email == "hello@example.com"
    assert user.email_verified is True
    assert user.is_private_email is None
