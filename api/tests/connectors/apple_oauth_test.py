import logging
from unittest.mock import MagicMock

import jwt
import pytest

from pcapi.connectors.apple_oauth import AppleSignInException
from pcapi.connectors.apple_oauth import build_encrypted_refresh_token
from pcapi.connectors.apple_oauth import get_apple_user
from pcapi.connectors.apple_oauth import revoke_refresh_token
from pcapi.utils import requests


def test_get_apple_user(mocker, requests_mock):
    mocker.patch("jwt.PyJWKClient.get_signing_key_from_jwt", return_value=MagicMock(key="fake-public-key"))
    mocker.patch("jwt.encode", return_value="eyFakeJwT")
    mocker.patch(
        "jwt.decode", return_value={"sub": "appleUserId", "email": "mail@example.com", "email_verified": "true"}
    )
    requests_mock.post(
        "https://appleid.apple.com/auth/token",
        status_code=200,
        json={"id_token": "eyEncodedIDToken", "refresh_token": "rt_apple"},
    )

    user, refresh_token = get_apple_user("valid_auth_code", is_web=True)

    assert user.sub == "appleUserId"
    assert user.email == "mail@example.com"
    assert user.email_verified is True
    assert user.is_private_email is None
    assert refresh_token == "rt_apple"


def test_get_apple_user_returns_none_refresh_token_when_missing(mocker, requests_mock):
    mocker.patch("jwt.PyJWKClient.get_signing_key_from_jwt", return_value=MagicMock(key="fake-public-key"))
    mocker.patch("jwt.encode", return_value="eyFakeJwT")
    mocker.patch(
        "jwt.decode", return_value={"sub": "appleUserId", "email": "mail@example.com", "email_verified": "true"}
    )
    requests_mock.post("https://appleid.apple.com/auth/token", status_code=200, json={"id_token": "eyEncodedIDToken"})

    _, refresh_token = get_apple_user("valid_auth_code", is_web=True)

    assert refresh_token is None


def test_get_apple_user_raises_apple_exception_when_id_token_missing(mocker, requests_mock):
    mocker.patch("jwt.encode", return_value="eyFakeJwT")
    requests_mock.post("https://appleid.apple.com/auth/token", status_code=200, json={"refresh_token": "rt_apple"})

    with pytest.raises(AppleSignInException):
        get_apple_user("valid_auth_code", is_web=True)


@pytest.mark.settings(APPLE_MOBILE_CLIENT_ID="apple.mobile.client", APPLE_WEB_CLIENT_ID="apple.web.client")
def test_revoke_refresh_token_succeeds_on_first_attempt(mocker, requests_mock):
    mocker.patch("jwt.encode", return_value="eyFakeClientSecret")
    matcher = requests_mock.post("https://appleid.apple.com/auth/revoke", status_code=200)

    revoke_refresh_token(build_encrypted_refresh_token("rt_apple", is_web=False))

    assert matcher.call_count == 1
    body = matcher.last_request.text
    assert "token=rt_apple" in body
    assert "token_type_hint=refresh_token" in body
    assert "client_id=apple.mobile.client" in body


@pytest.mark.settings(APPLE_MOBILE_CLIENT_ID="apple.mobile.client", APPLE_WEB_CLIENT_ID="apple.web.client")
def test_revoke_refresh_token_tries_issuing_client_id_first(mocker, requests_mock):
    mocker.patch("jwt.encode", return_value="eyFakeClientSecret")
    matcher = requests_mock.post("https://appleid.apple.com/auth/revoke", status_code=200)

    revoke_refresh_token(build_encrypted_refresh_token("rt_apple", is_web=True))

    assert matcher.call_count == 1
    assert "client_id=apple.web.client" in matcher.last_request.text


@pytest.mark.settings(APPLE_MOBILE_CLIENT_ID="apple.mobile.client", APPLE_WEB_CLIENT_ID="apple.web.client")
def test_revoke_refresh_token_falls_back_to_other_client(mocker, requests_mock):
    mocker.patch("jwt.encode", return_value="eyFakeClientSecret")
    matcher = requests_mock.post(
        "https://appleid.apple.com/auth/revoke",
        [{"status_code": 400, "reason": "Bad request"}, {"status_code": 200}],
    )

    revoke_refresh_token(build_encrypted_refresh_token("rt_apple", is_web=False))

    assert matcher.call_count == 2
    assert "client_id=apple.web.client" in matcher.last_request.text


@pytest.mark.settings(APPLE_MOBILE_CLIENT_ID="apple.mobile.client", APPLE_WEB_CLIENT_ID="apple.web.client")
def test_revoke_refresh_token_does_not_fall_back_on_transport_error(mocker, requests_mock):
    mocker.patch("jwt.encode", return_value="eyFakeClientSecret")
    matcher = requests_mock.post(
        "https://appleid.apple.com/auth/revoke",
        [{"exc": requests.exceptions.ConnectTimeout}, {"status_code": 200}],
    )

    # A transport failure means the endpoint is unreachable: retrying the same endpoint with the
    # other client_id would only hold row locks longer, so the error propagates immediately.
    with pytest.raises(requests.exceptions.ConnectTimeout):
        revoke_refresh_token(build_encrypted_refresh_token("rt_apple", is_web=False))

    assert matcher.call_count == 1


@pytest.mark.settings(APPLE_MOBILE_CLIENT_ID="apple.mobile.client", APPLE_WEB_CLIENT_ID="apple.web.client")
def test_revoke_refresh_token_raises_when_all_attempts_fail(mocker, requests_mock):
    mocker.patch("jwt.encode", return_value="eyFakeClientSecret")
    requests_mock.post("https://appleid.apple.com/auth/revoke", status_code=400, reason="Bad request")

    with pytest.raises(requests.exceptions.HTTPError):
        revoke_refresh_token(build_encrypted_refresh_token("rt_apple", is_web=False))


def test_logs_and_raises_on_fetch_id_token_bad_request(mocker, requests_mock, caplog):
    mocker.patch("jwt.PyJWKClient.get_signing_key_from_jwt", return_value=MagicMock(key="fake-public-key"))
    mocker.patch("jwt.encode", return_value="eyFakeJwT")
    mocker.patch(
        "jwt.decode", return_value={"sub": "appleUserId", "email": "mail@example.com", "email_verified": "true"}
    )
    requests_mock.post("https://appleid.apple.com/auth/token", status_code=400, reason="Bad request")

    with caplog.at_level(logging.ERROR):
        with pytest.raises(AppleSignInException):
            get_apple_user("valid_auth_code", is_web=True)

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
            get_apple_user("valid_auth_code", is_web=True)

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
            get_apple_user("valid_auth_code", is_web=True)

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
            get_apple_user("valid_auth_code", is_web=True)

    assert caplog.records[0].extra["error"] == "The JWKS endpoint did not return a JSON object"


def test_logs_and_raises_on_id_token_decoding_error(mocker, requests_mock, caplog):
    mocker.patch("jwt.PyJWKClient.get_signing_key_from_jwt", return_value=MagicMock(key="fake-public-key"))
    mocker.patch("jwt.encode", return_value="eyFakeJwT")
    mocker.patch("jwt.decode", side_effect=jwt.InvalidSignatureError("Signature verification failed"))
    requests_mock.post("https://appleid.apple.com/auth/token", status_code=200, json={"id_token": "eyEncodedIDToken"})

    with caplog.at_level(logging.ERROR):
        with pytest.raises(AppleSignInException):
            get_apple_user("valid_auth_code", is_web=True)

    assert caplog.records[0].extra["error_type"] == "InvalidSignatureError"
    assert caplog.records[0].extra["error"] == "Signature verification failed"
