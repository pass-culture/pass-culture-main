from datetime import datetime

import jwt

from pcapi import settings
from pcapi.core.users.models import ALGORITHM_HS_256
from pcapi.core.users.utils import create_custom_jwt_token
from pcapi.core.users.utils import encode_jwt_payload


class CreateCustomJwtTokenTest:
    def test_create_custom_jwt_token(self):
        user_id = 11
        token_type = "test-token"
        expiration_date = datetime.now()

        jwt_token = create_custom_jwt_token(user_id, token_type, expiration_date)

        decoded = jwt.decode(jwt_token, settings.JWT_SECRET_KEY, algorithms=ALGORITHM_HS_256)

        assert decoded["userId"] == user_id
        assert decoded["type"] == token_type
        assert decoded["exp"] == int(expiration_date.timestamp())

    def test_create_custom_jwt_token_without_expiration_date(self):
        user_id = 11
        token_type = "test-token"

        jwt_token = create_custom_jwt_token(user_id, token_type)

        decoded = jwt.decode(jwt_token, settings.JWT_SECRET_KEY, algorithms=ALGORITHM_HS_256)

        assert decoded["userId"] == user_id
        assert decoded["type"] == token_type
        assert "exp" not in decoded

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
