from base64 import b64encode
from time import time

import jwt
import pytest

from pcapi import settings
from pcapi.utils.jwt import ALGORITHM_HS_256
from pcapi.utils.jwt.backends.simple import JwtSimpleBackend


class InitializationTest:
    def test_nominal(self):
        assert JwtSimpleBackend()

    @pytest.mark.settings(JWT_SECRET_KEY="")
    def test_no_secret_key(self):
        with pytest.raises(ValueError):
            JwtSimpleBackend()


class EncodeTest:
    def test_nominal(self):
        payload = {"iat": int(time()), "nbf": int(time()), "exp": int(time()) + 60, "data": "plouf"}

        token = JwtSimpleBackend().encode(payload)

        assert jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[ALGORITHM_HS_256]) == payload
        assert token.split(".")[0] == b64encode(b'{"alg":"HS256","typ":"JWT"}').decode().strip("=")

    def test_missing_fields(self):
        payload = {"data": "plouf"}

        token = JwtSimpleBackend().encode(payload)

        decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[ALGORITHM_HS_256])
        assert decoded["data"] == payload["data"]
        assert time() - 2 < decoded["iat"] < time()
        assert time() - 2 < decoded["nbf"] < time()
        assert decoded["exp"] > time()

    def test_custom_key(self):
        key = "a-secret-key"
        payload = {"iat": int(time()), "nbf": int(time()), "exp": int(time()) + 60, "data": "plouf"}

        token = JwtSimpleBackend().encode(payload, key)

        assert jwt.decode(token, key, algorithms=[ALGORITHM_HS_256]) == payload


class DecodeTest:
    def test_nominal(self):
        payload = {
            "token": "value",
        }
        token = jwt.encode(payload, settings.JWT_SECRET_KEY)

        decoded = JwtSimpleBackend().decode(jwt_token=token)

        assert decoded == payload

    def test_decode_with_invalid_key(self):
        payload = {
            "token": "value",
        }
        token = jwt.encode(payload, "an-invalid-key")

        with pytest.raises(jwt.exceptions.InvalidSignatureError):
            JwtSimpleBackend().decode(jwt_token=token)

    def test_malformed_token(self):
        with pytest.raises(jwt.exceptions.InvalidTokenError):
            JwtSimpleBackend().decode(jwt_token="not a token")

    def decode_with_custom_key(self):
        custom_key = "a-random-key-without-data"
        payload = {
            "token": "value",
        }
        token = jwt.encode(payload, custom_key)

        decoded = JwtSimpleBackend().decode(jwt_token=token, key=custom_key)

        assert decoded == payload
