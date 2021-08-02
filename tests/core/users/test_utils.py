from datetime import datetime

import jwt
import pytest

from pcapi import settings
from pcapi.core.users.factories import UserFactory
from pcapi.core.users.models import ALGORITHM_RS_256
from pcapi.core.users.utils import ALGORITHM_HS_256
from pcapi.core.users.utils import decode_jwt_token_rs256
from pcapi.core.users.utils import encode_jwt_payload
from pcapi.core.users.utils import format_phone_number_with_country_code

from tests.routes.adage_iframe import INVALID_RSA_PRIVATE_KEY_PATH
from tests.routes.adage_iframe import VALID_RSA_PRIVATE_KEY_PATH


class EncodeJWTPayloadTest:
    def test_encode_jwt_payload(self):
        payload = dict(data="value")
        expiration_date = datetime.now()

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

        decoded = decode_jwt_token_rs256(valid_encoded_token)

        assert decoded["data"] == "value"

    def test_decode_jwt_payload_rs256_algorithm_corrupted(self):
        payload = dict(data="value")
        with open(INVALID_RSA_PRIVATE_KEY_PATH, "rb") as reader:
            corrupted_token = jwt.encode(payload, key=reader.read(), algorithm=ALGORITHM_RS_256)

        with pytest.raises(jwt.InvalidSignatureError) as error:
            decode_jwt_token_rs256(corrupted_token)

        assert "Signature verification failed" in str(error.value)


@pytest.mark.usefixtures("db_session")
class FormatPhoneNumberTest:
    def test_format_phone_number(self):
        user = UserFactory(phoneNumber="0602030405")

        assert format_phone_number_with_country_code(user) == "33602030405"

    def test_format_phone_number_guyana(self):
        user = UserFactory(phoneNumber="0602030405", postalCode="97304", departementCode="973")

        assert format_phone_number_with_country_code(user) == "594602030405"
