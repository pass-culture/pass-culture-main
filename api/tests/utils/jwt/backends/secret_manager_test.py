import string
from base64 import b64encode
from dataclasses import dataclass
from datetime import datetime
from random import choices
from time import time
from unittest import mock

import jwt
import pytest
from flask import current_app
from google.cloud.secretmanager_v1.types import resources as google_types

from pcapi import settings
from pcapi.utils.jwt import ALGORITHM_HS_256
from pcapi.utils.jwt.backends.secret_manager import REDIS_KEY
from pcapi.utils.jwt.backends.secret_manager import JwtSecretManagerBackend


@dataclass
class _ListSecretVersions:
    versions: list
    next_page_token: str = ""

    def __iter__(self):
        for version in self.versions:
            yield version


@dataclass
class _Version:
    state: google_types.SecretVersion.State
    name: str
    create_time: datetime


@dataclass
class _Payload:
    data: bytes


@dataclass
class _Secret:
    payload: _Payload


NEXT_PAGE_TOKEN = "".join(choices(string.ascii_uppercase + string.digits, k=25))
VERSIONS = [
    _Version(
        state=google_types.SecretVersion.State.ENABLED,
        name=settings.JWT_KEY_SECRET_NAME + "/4",
        create_time=datetime(2026, 12, 1),
    ),
    _Version(
        state=google_types.SecretVersion.State.DISABLED,
        name=settings.JWT_KEY_SECRET_NAME + "/3",
        create_time=datetime(2026, 11, 1),
    ),
    _Version(
        state=google_types.SecretVersion.State.DESTROYED,
        name=settings.JWT_KEY_SECRET_NAME + "/2",
        create_time=datetime(2026, 10, 1),
    ),
    _Version(
        state=google_types.SecretVersion.State.ENABLED,
        name=settings.JWT_KEY_SECRET_NAME + "/1",
        create_time=datetime(2026, 9, 1),
    ),
]
SECRETS = {
    "1": _Secret(payload=_Payload(data=b"secret-with-id-one")),
    "3": _Secret(payload=_Payload(data=b"secret-with-id-three")),
    "4": _Secret(payload=_Payload(data=b"secret-with-id-four")),
}


def _list_secret_versions(request):
    if request.page_token:
        if request.page_token != NEXT_PAGE_TOKEN:
            assert False, "invalid next page token recieved"
        return _ListSecretVersions(versions=VERSIONS[2:])
    return _ListSecretVersions(versions=VERSIONS[:2], next_page_token=NEXT_PAGE_TOKEN)


@pytest.fixture
def secret_manager():
    SecretManagerServiceClientMock = mock.MagicMock()
    SecretManagerServiceClientMock.list_secret_versions.side_effect = _list_secret_versions
    SecretManagerServiceClientMock.access_secret_version.side_effect = lambda request: SECRETS[request.name[-1]]
    with mock.patch(
        "pcapi.utils.jwt.backends.secret_manager.secretmanager.SecretManagerServiceClient",
        return_value=SecretManagerServiceClientMock,
    ):
        yield

    assert SecretManagerServiceClientMock.list_secret_versions.call_count == 2
    assert SecretManagerServiceClientMock.access_secret_version.call_count == 2


class InitializationTest:
    def test_nominal(self, secret_manager):
        backend = JwtSecretManagerBackend()
        assert backend._current_key.kid == "1796083200"
        assert backend._current_key.key == "secret-with-id-four"
        assert backend._key_by_kid == {
            "1796083200": "secret-with-id-four",
            "1788220800": "secret-with-id-one",
        }

    @pytest.mark.settings(JWT_SECRET_KEY="")
    def test_no_legacy_secret_key(self):
        with pytest.raises(ValueError):
            JwtSecretManagerBackend()

    @pytest.mark.settings(JWT_KEY_SECRET_NAME="")
    def test_no_secret_name(self):
        with pytest.raises(ValueError):
            JwtSecretManagerBackend()

    def test_no_secret_manager_fallback_redis(self, clear_redis):
        redis_mapping = {"123": "a key", "456": "another key"}
        current_app.redis_client.hset(REDIS_KEY, mapping=redis_mapping)

        with mock.patch(
            "pcapi.utils.jwt.backends.secret_manager.secretmanager.SecretManagerServiceClient",
            side_effect=Exception,
        ):
            backend = JwtSecretManagerBackend()

        assert backend._key_by_kid == redis_mapping
        assert backend._current_key.kid == "456"
        assert backend._current_key.key == "another key"

    def test_no_secret_manager_no_redis(self, clear_redis):
        with mock.patch(
            "pcapi.utils.jwt.backends.secret_manager.secretmanager.SecretManagerServiceClient",
            side_effect=Exception,
        ):
            with pytest.raises(ValueError):
                JwtSecretManagerBackend()


class EncodeTest:
    def test_nominal(self, secret_manager):
        payload = {"iat": int(time()), "nbf": int(time()), "exp": int(time()) + 60, "data": "plouf"}

        token = JwtSecretManagerBackend().encode(payload)

        assert jwt.decode(token, "secret-with-id-four", algorithms=[ALGORITHM_HS_256]) == payload
        assert token.split(".")[0] == b64encode(b'{"alg":"HS256","kid":"1796083200","typ":"JWT"}').decode().strip("=")

    def test_missing_fields(self, secret_manager):
        payload = {"data": "plouf"}

        token = JwtSecretManagerBackend().encode(payload)

        decoded = jwt.decode(token, "secret-with-id-four", algorithms=[ALGORITHM_HS_256])
        assert decoded["data"] == payload["data"]
        assert time() - 2 < decoded["iat"] < time()
        assert time() - 2 < decoded["nbf"] < time()
        assert decoded["exp"] > time()

    def test_custom_key(self, secret_manager):
        key = "a-secret-key"
        payload = {"iat": int(time()), "nbf": int(time()), "exp": int(time()) + 60, "data": "plouf"}

        token = JwtSecretManagerBackend().encode(payload, key)

        assert jwt.decode(token, key, algorithms=[ALGORITHM_HS_256]) == payload
        assert token.split(".")[0] == b64encode(b'{"alg":"HS256","typ":"JWT"}').decode().strip("=")


class DecodeTest:
    def test_nominal(self, secret_manager):
        payload = {
            "token": "value",
        }
        token = jwt.encode(payload, "secret-with-id-four", headers={"kid": "1796083200"})

        decoded = JwtSecretManagerBackend().decode(jwt_token=token)

        assert decoded == payload

    def test_old_key(self, secret_manager):
        payload = {
            "token": "value",
        }
        token = jwt.encode(payload, "secret-with-id-one", headers={"kid": "1788220800"})

        decoded = JwtSecretManagerBackend().decode(jwt_token=token)

        assert decoded == payload

    def test_invalid_kid(self, secret_manager):
        payload = {
            "token": "value",
        }
        token = jwt.encode(payload, "secret-with-id-four", headers={"kid": "invalid"})

        with pytest.raises(jwt.exceptions.InvalidKeyError):
            JwtSecretManagerBackend().decode(jwt_token=token)

    def test_wrong_kid(self, secret_manager):
        payload = {
            "token": "value",
        }
        token = jwt.encode(payload, "secret-with-id-four", headers={"kid": "1788220800"})

        with pytest.raises(jwt.exceptions.InvalidTokenError):
            JwtSecretManagerBackend().decode(jwt_token=token)

    def test_no_kid(self, secret_manager):
        payload = {
            "token": "value",
        }
        token = jwt.encode(payload, settings.JWT_SECRET_KEY)

        decoded = JwtSecretManagerBackend().decode(jwt_token=token)

        assert decoded == payload

    def test_decode_with_invalid_key(self, secret_manager):
        payload = {
            "token": "value",
        }
        token = jwt.encode(payload, "an-invalid-key")

        with pytest.raises(jwt.exceptions.InvalidSignatureError):
            JwtSecretManagerBackend().decode(jwt_token=token)

    def test_malformed_token(self, secret_manager):
        with pytest.raises(jwt.exceptions.InvalidTokenError):
            JwtSecretManagerBackend().decode(jwt_token="not a token")

    def decode_with_custom_key(self, secret_manager):
        custom_key = "a-random-key-without-data"
        payload = {
            "token": "value",
        }
        token = jwt.encode(payload, custom_key)

        decoded = JwtSecretManagerBackend().decode(jwt_token=token, key=custom_key)

        assert decoded == payload


# TODO test on redis fallback
