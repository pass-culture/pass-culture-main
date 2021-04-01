from datetime import datetime

import jwt

from pcapi import settings
from pcapi.core.users.utils import ALGORITHM_HS_256
from pcapi.core.users.utils import encode_jwt_payload


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
