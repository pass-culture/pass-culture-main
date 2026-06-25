import datetime
import time

import jwt
import pytest

from pcapi import settings
from pcapi.utils import date as date_utils
from pcapi.utils.jwt import ALGORITHM_HS_256
from pcapi.utils.jwt import ALGORITHM_RS_256
from pcapi.utils.jwt import JWT_ADAGE_PUBLIC_KEY_PATH
from pcapi.utils.jwt import decode_jwt_token
from pcapi.utils.jwt import decode_jwt_token_rs256
from pcapi.utils.jwt import encode_jwt_payload

from tests.routes.adage_iframe import INVALID_RSA_PRIVATE_KEY_PATH
from tests.routes.adage_iframe import VALID_RSA_PRIVATE_KEY_PATH


class EncodeJWTPayloadTest:
    def test_encode_jwt_payload(self):
        payload = dict(data="value")
        expiration_date = date_utils.get_naive_utc_now() + datetime.timedelta(days=1)
        start = int(time.time())
        jwt_token = encode_jwt_payload(payload, expiration_date)

        decoded = jwt.decode(jwt_token, settings.JWT_SECRET_KEY, algorithms=ALGORITHM_HS_256)

        assert decoded["data"] == "value"
        assert decoded["exp"] == int(expiration_date.timestamp())
        assert decoded["nbf"] <= start + 1
        assert decoded["nbf"] >= start
        assert decoded["iat"] == decoded["nbf"]
        assert len(decoded) == 4

    def test_force_expiration(self):
        jwt_token = encode_jwt_payload({})

        decoded = jwt.decode(jwt_token, settings.JWT_SECRET_KEY, algorithms=ALGORITHM_HS_256)

        assert "exp" in decoded
        assert decoded["exp"] == decoded["nbf"] + 20 * 60


class DecodeJWTTokenTest:
    def test_decode_jwt_token(self):
        token = jwt.encode({"data": "value"}, key=settings.JWT_SECRET_KEY, algorithm=ALGORITHM_HS_256)

        decoded = decode_jwt_token(token)

        assert decoded["data"] == "value"

    def test_decode_jwt_token_invalid_key(self):
        token = jwt.encode({"data": "value"}, key="secret jwt key", algorithm=ALGORITHM_HS_256)

        with pytest.raises(jwt.exceptions.InvalidSignatureError):
            decode_jwt_token(token)

    def test_decode_jwt_token_before_nbf(self):
        token = jwt.encode({"nbf": int(time.time()) + 60}, key=settings.JWT_SECRET_KEY, algorithm=ALGORITHM_HS_256)

        with pytest.raises(jwt.exceptions.ImmatureSignatureError):
            decode_jwt_token(token)

    def test_decode_jwt_token_before_iat(self):
        token = jwt.encode({"iat": int(time.time()) + 60}, key=settings.JWT_SECRET_KEY, algorithm=ALGORITHM_HS_256)

        with pytest.raises(jwt.exceptions.ImmatureSignatureError):
            decode_jwt_token(token)

    def test_decode_jwt_token_after_exp(self):
        token = jwt.encode({"exp": int(time.time()) - 60}, key=settings.JWT_SECRET_KEY, algorithm=ALGORITHM_HS_256)

        with pytest.raises(jwt.exceptions.ExpiredSignatureError):
            decode_jwt_token(token)


class DecodeJWTPayloadRS256Test:
    def test_decode_jwt_payload_rs256_algorithm(self):
        payload = dict(data="value")
        with open(VALID_RSA_PRIVATE_KEY_PATH, "rb") as reader:
            valid_encoded_token = jwt.encode(payload, key=reader.read(), algorithm=ALGORITHM_RS_256)
        with open(JWT_ADAGE_PUBLIC_KEY_PATH, "rb") as reader:
            public_key = reader.read()
            decoded = decode_jwt_token_rs256(valid_encoded_token, public_key)

        assert decoded["data"] == "value"

    def test_decode_jwt_payload_rs256_algorithm_corrupted(self):
        payload = dict(data="value")
        with open(INVALID_RSA_PRIVATE_KEY_PATH, "rb") as reader:
            corrupted_token = jwt.encode(payload, key=reader.read(), algorithm=ALGORITHM_RS_256)

        with pytest.raises(jwt.InvalidSignatureError) as error:
            with open(JWT_ADAGE_PUBLIC_KEY_PATH, "rb") as reader:
                public_key = reader.read()
                decode_jwt_token_rs256(corrupted_token, public_key=public_key)

        assert "Signature verification failed" in str(error.value)
