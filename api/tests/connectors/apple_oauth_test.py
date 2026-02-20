import logging
from unittest.mock import MagicMock

import jwt
import pytest

from pcapi.connectors.apple_oauth import AppleSignInException
from pcapi.connectors.apple_oauth import get_apple_user
from pcapi.utils import requests


def test_get_apple_user(mocker, requests_mock):
    mocker.patch("jwt.PyJWKClient.get_signing_key_from_jwt", return_value=MagicMock(key="fake-public-key"))
    mocker.patch("jwt.encode", return_value="eyFakeJwT")
    mocker.patch(
        "jwt.decode", return_value={"sub": "appleUserId", "email": "mail@example.com", "email_verified": "true"}
    )
    requests_mock.post("https://appleid.apple.com/auth/token", status_code=200, json={"id_token": "eyEncodedIDToken"})

    user = get_apple_user("valid_auth_code")

    assert user.sub == "appleUserId"
    assert user.email == "mail@example.com"
    assert user.email_verified is True
    assert user.is_private_email is None


def test_logs_and_raises_on_fetch_id_token_bad_request(mocker, requests_mock, caplog):
    mocker.patch("jwt.PyJWKClient.get_signing_key_from_jwt", return_value=MagicMock(key="fake-public-key"))
    mocker.patch("jwt.encode", return_value="eyFakeJwT")
    mocker.patch(
        "jwt.decode", return_value={"sub": "appleUserId", "email": "mail@example.com", "email_verified": "true"}
    )
    requests_mock.post("https://appleid.apple.com/auth/token", status_code=400, reason="Bad request")

    with caplog.at_level(logging.ERROR):
        with pytest.raises(AppleSignInException):
            get_apple_user("valid_auth_code")

    assert caplog.records[0].extra["status_code"] == 400
    assert "Bad request" in caplog.records[0].extra["response"]
    assert "https://appleid.apple.com/auth/token" in caplog.records[0].extra["response"]


def test_logs_and_raises_on_fetch_id_token_network_error(mocker, caplog):
    mocker.patch("jwt.PyJWKClient.get_signing_key_from_jwt", return_value=MagicMock(key="fake-public-key"))
    mocker.patch("jwt.encode", return_value="eyFakeJwT")
    mocker.patch(
        "jwt.decode", return_value={"sub": "appleUserId", "email": "mail@example.com", "email_verified": "true"}
    )
    mocker.patch("pcapi.connectors.apple_oauth.requests.post", side_effect=requests.exceptions.RequestException)

    with caplog.at_level(logging.ERROR):
        with pytest.raises(AppleSignInException):
            get_apple_user("valid_auth_code")

    assert "Network error" in caplog.records[0].message


def test_logs_and_raises_on_fetch_id_token_bad_response(mocker, caplog):
    mocker.patch("jwt.PyJWKClient.get_signing_key_from_jwt", return_value=MagicMock(key="fake-public-key"))
    mocker.patch("jwt.encode", return_value="eyFakeJwT")
    mocker.patch(
        "jwt.decode", return_value={"sub": "appleUserId", "email": "mail@example.com", "email_verified": "true"}
    )
    mocker.patch("pcapi.connectors.apple_oauth.requests.post", side_effect=ValueError)

    with caplog.at_level(logging.ERROR):
        with pytest.raises(AppleSignInException):
            get_apple_user("valid_auth_code")

    assert "Malformed response" in caplog.records[0].message


def test_logs_and_raises_on_get_signing_key_error(mocker, requests_mock, caplog):
    mocker.patch(
        "jwt.PyJWKClient.get_signing_key_from_jwt",
        side_effect=jwt.PyJWKClientError("The JWKS endpoint did not return a JSON object"),
    )
    mocker.patch("jwt.encode", return_value="eyFakeJwT")
    requests_mock.post("https://appleid.apple.com/auth/token", status_code=200, json={"id_token": "eyEncodedIDToken"})

    with caplog.at_level(logging.ERROR):
        with pytest.raises(AppleSignInException):
            get_apple_user("valid_auth_code")

    assert caplog.records[0].extra["error"] == "The JWKS endpoint did not return a JSON object"


def test_logs_and_raises_on_id_token_decoding_error(mocker, requests_mock, caplog):
    mocker.patch("jwt.PyJWKClient.get_signing_key_from_jwt", return_value=MagicMock(key="fake-public-key"))
    mocker.patch("jwt.encode", return_value="eyFakeJwT")
    mocker.patch("jwt.decode", side_effect=jwt.InvalidSignatureError("Signature verification failed"))
    requests_mock.post("https://appleid.apple.com/auth/token", status_code=200, json={"id_token": "eyEncodedIDToken"})

    with caplog.at_level(logging.ERROR):
        with pytest.raises(AppleSignInException):
            get_apple_user("valid_auth_code")

    assert caplog.records[0].extra["error_type"] == "InvalidSignatureError"
    assert caplog.records[0].extra["error"] == "Signature verification failed"
