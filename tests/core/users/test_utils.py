from datetime import datetime

import jwt

from pcapi.core.users.models import ALGORITHM_HS_256
from pcapi.core.users.utils import create_custom_jwt_token
from pcapi.flask_app import jwt_secret_key


class CreateCurstomJwtTokenTest:
    def test_create_curstom_jwt_token(self):
        user_id = 11
        token_type = "test-token"
        expiration_date = datetime.now()

        jwt_token = create_custom_jwt_token(user_id, token_type, expiration_date)

        decoded = jwt.decode(jwt_token, jwt_secret_key, algorithms=ALGORITHM_HS_256)

        assert decoded["userId"] == user_id
        assert decoded["type"] == token_type
        assert decoded["exp"] == int(expiration_date.timestamp())

    def test_create_curstom_jwt_token_without_expiration_date(self):
        user_id = 11
        token_type = "test-token"

        jwt_token = create_custom_jwt_token(user_id, token_type)

        decoded = jwt.decode(jwt_token, jwt_secret_key, algorithms=ALGORITHM_HS_256)

        assert decoded["userId"] == user_id
        assert decoded["type"] == token_type
        assert "exp" not in decoded
