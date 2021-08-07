import datetime
from typing import ByteString

import jwt

from pcapi.core.users.models import ALGORITHM_RS_256

from tests.routes.adage_iframe import VALID_RSA_PRIVATE_KEY_PATH


def create_adage_jwt_fake_valid_token(user_email: str = None) -> ByteString:
    now = datetime.datetime.utcnow()
    with open(VALID_RSA_PRIVATE_KEY_PATH, "rb") as reader:
        return jwt.encode(
            {"email": user_email, "exp": now + datetime.timedelta(days=1)},
            key=reader.read(),
            algorithm=ALGORITHM_RS_256,
        )
