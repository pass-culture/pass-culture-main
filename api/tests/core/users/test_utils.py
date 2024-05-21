import datetime

import jwt
import pytest

from pcapi import settings
from pcapi.core.users import utils as user_utils
from pcapi.core.users.utils import ALGORITHM_HS_256
from pcapi.core.users.utils import ALGORITHM_RS_256
from pcapi.core.users.utils import decode_jwt_token_rs256
from pcapi.core.users.utils import encode_jwt_payload
from pcapi.core.users.utils import format_login_location

from tests.routes.adage_iframe import INVALID_RSA_PRIVATE_KEY_PATH
from tests.routes.adage_iframe import VALID_RSA_PRIVATE_KEY_PATH


class EncodeJWTPayloadTest:
    def test_encode_jwt_payload(self):
        payload = dict(data="value")
        expiration_date = datetime.datetime.utcnow() + datetime.timedelta(days=1)

        jwt_token = encode_jwt_payload(payload, expiration_date)

        decoded = jwt.decode(jwt_token, settings.JWT_SECRET_KEY, algorithms=ALGORITHM_HS_256)

        assert decoded == {"data": "value", "exp": int(expiration_date.timestamp())}

    def test_encode_jwt_payload_without_expiration_date(self):
        payload = dict(data="value")

        jwt_token = encode_jwt_payload(payload)

        decoded = jwt.decode(jwt_token, settings.JWT_SECRET_KEY, algorithms=ALGORITHM_HS_256)

        assert decoded["data"] == "value"
        assert "exp" not in decoded


class DecodeJWTPayloadRS256Test:
    def test_decode_jwt_payload_rs256_algorithm(self):
        payload = dict(data="value")
        with open(VALID_RSA_PRIVATE_KEY_PATH, "rb") as reader:

            valid_encoded_token = jwt.encode(payload, key=reader.read(), algorithm=ALGORITHM_RS_256)
        with open(user_utils.JWT_ADAGE_PUBLIC_KEY_PATH, "rb") as reader:
            public_key = reader.read()
            decoded = decode_jwt_token_rs256(valid_encoded_token, public_key)

        assert decoded["data"] == "value"

    def test_decode_jwt_payload_rs256_algorithm_corrupted(self):
        payload = dict(data="value")
        with open(INVALID_RSA_PRIVATE_KEY_PATH, "rb") as reader:
            corrupted_token = jwt.encode(payload, key=reader.read(), algorithm=ALGORITHM_RS_256)

        with pytest.raises(jwt.InvalidSignatureError) as error:
            with open(user_utils.JWT_ADAGE_PUBLIC_KEY_PATH, "rb") as reader:
                public_key = reader.read()
                decode_jwt_token_rs256(corrupted_token, public_key=public_key)

        assert "Signature verification failed" in str(error.value)


class FormatLoginLocationTest:
    @pytest.mark.parametrize("country_name", ["France", None])
    def should_return_country_name_when_no_city_name(self, country_name):
        assert format_login_location(country_name, city_name=None) == country_name

    @pytest.mark.parametrize("city_name", ["Paris", None])
    def should_return_city_name_when_no_country_name(self, city_name):
        assert format_login_location(country_name=None, city_name=city_name) == city_name

    def should_return_country_and_city_separated_by_comma_when_both_are_available(self):
        assert format_login_location(country_name="France", city_name="Paris") == "Paris, France"
