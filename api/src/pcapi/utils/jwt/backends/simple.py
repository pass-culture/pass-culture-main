import jwt

from pcapi import settings
from pcapi.utils.jwt.backends.base import JwtBaseBackend


class JwtSimpleBackend(JwtBaseBackend):
    def __init__(self) -> None:
        if not settings.JWT_SECRET_KEY:
            raise ValueError("JWT_SECRET_KEY not found in env")

    def encode(self, payload: dict, key: str | None = None) -> str:
        from pcapi.utils.jwt import ALGORITHM_HS_256

        key = key if key is not None else settings.JWT_SECRET_KEY

        return jwt.encode(
            payload=self._complete_payload(payload),
            key=key,
            algorithm=ALGORITHM_HS_256,
        )

    def decode(self, jwt_token: str, key: str | None = None) -> dict:
        from pcapi.utils.jwt import ALGORITHM_HS_256

        key = key if key is not None else settings.JWT_SECRET_KEY

        return jwt.decode(
            jwt=jwt_token,
            key=key,
            algorithms=[ALGORITHM_HS_256],
        )
