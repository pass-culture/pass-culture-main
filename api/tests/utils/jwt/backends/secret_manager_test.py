from base64 import b64encode
from time import time
from unittest import mock

import jwt
import pytest
from flask import current_app

from pcapi import settings
from pcapi.connectors import google_secret_manager
from pcapi.utils.jwt import ALGORITHM_HS_256
from pcapi.utils.jwt.backends.secret_manager import REDIS_KEY
from pcapi.utils.jwt.backends.secret_manager import JwtSecretManagerBackend


SECRETS = {
    "1": "secret-with-id-one",
    "3": "secret-with-id-three",
    "4": "secret-with-id-four",
}


def _get_last_secret_versions(secret_name, limit):
    for key, value in SECRETS.items():
        yield google_secret_manager.Secret(
            name=f"{secret_name}/{key}",
            creation_timestamp=int(key),
            value=value,
        )


@pytest.fixture
def secret_manager():
    secret_manager_backend = mock.MagicMock()
    secret_manager_backend.get_last_secret_versions = _get_last_secret_versions

    with mock.patch(
        "pcapi.utils.jwt.backends.secret_manager.SecretManagerBackend",
        return_value=secret_manager_backend,
    ):
        yield


class InitializationTest:
    def test_nominal(self, secret_manager):
        backend = JwtSecretManagerBackend()
        assert backend._current_key.kid == "4"
        assert backend._current_key.key == "secret-with-id-four"
        assert backend._key_by_kid == {
            "4": "secret-with-id-four",
            "3": "secret-with-id-three",
            "1": "secret-with-id-one",
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
            "pcapi.utils.jwt.backends.secret_manager.SecretManagerBackend.get_last_secret_versions",
            side_effect=google_secret_manager.SecretManagerException,
        ):
            backend = JwtSecretManagerBackend()

        assert backend._key_by_kid == redis_mapping
        assert backend._current_key.kid == "456"
        assert backend._current_key.key == "another key"

    def test_no_secret_manager_no_redis(self, clear_redis):
        with mock.patch(
            "pcapi.utils.jwt.backends.secret_manager.SecretManagerBackend.get_last_secret_versions",
            side_effect=google_secret_manager.SecretManagerException,
        ):
            with pytest.raises(ValueError):
                JwtSecretManagerBackend()


class EncodeTest:
    def test_nominal(self, secret_manager):
        payload = {"iat": int(time()), "nbf": int(time()), "exp": int(time()) + 60, "data": "plouf"}

        token = JwtSecretManagerBackend().encode(payload)

        assert jwt.decode(token, "secret-with-id-four", algorithms=[ALGORITHM_HS_256]) == payload
        assert token.split(".")[0] == b64encode(b'{"alg":"HS256","kid":"4","typ":"JWT"}').decode().strip("=")

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
        token = jwt.encode(payload, "secret-with-id-four", headers={"kid": "4"})

        decoded = JwtSecretManagerBackend().decode(jwt_token=token)

        assert decoded == payload

    def test_old_key(self, secret_manager):
        payload = {
            "token": "value",
        }
        token = jwt.encode(payload, "secret-with-id-one", headers={"kid": "1"})

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
        token = jwt.encode(payload, "secret-with-id-four", headers={"kid": "1"})

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
