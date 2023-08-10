import dataclasses
from datetime import datetime
from datetime import timedelta
import enum
import logging
from typing import Type
from typing import TypeVar

from flask import current_app as app
import jwt

from pcapi.core.users import utils
from pcapi.core.users.exceptions import InvalidToken


logger = logging.getLogger(__name__)


class TokenType(enum.Enum):
    EMAIL_CHANGE_CONFIRMATION = "update_email_confirmation"
    EMAIL_CHANGE_VALIDATION = "update_email_validation"


@dataclasses.dataclass(frozen=True)
class Token:
    type_: TokenType
    user_id: int
    encoded_token: str
    data: dict

    class _TokenAction(enum.Enum):
        CHECK_OK = "check_ok"
        CHECK_KO = "check_ko"
        EXPIRE = "expire"
        CREATE = "create"

    @classmethod
    def load_without_checking(cls, encoded_token: str) -> "Token":
        try:
            payload = utils.decode_jwt_token(encoded_token)
        except jwt.PyJWTError:
            raise InvalidToken()
        try:
            data = payload["data"] if payload["data"] is not None else {}
            type_ = TokenType(payload["token_type"])
            user_id = payload["user_id"]
            return cls(type_, user_id, encoded_token, data)
        except (KeyError, ValueError):
            raise InvalidToken()

    @classmethod
    def _get_redis_key(cls, type_: TokenType, user_id: int) -> str:
        return f"pcapi:token:{type_.value}_{user_id}"

    @classmethod
    def get_expiration_date(cls, type_: TokenType, user_id: int) -> datetime | None:
        key = Token._get_redis_key(type_, user_id)
        ttl = app.redis_client.ttl(key)  # type: ignore [attr-defined]
        if ttl < 0:
            # -2 if doesn't exist, -1 if no expiration
            return None
        return datetime.utcnow() + timedelta(seconds=ttl)

    def check(self, type_: TokenType, user_id: int | None = None) -> None:
        redis_key = Token._get_redis_key(self.type_, self.user_id)
        if (
            self.type_ != type_
            or (user_id is not None and self.user_id != user_id)
            or app.redis_client.get(redis_key) != self.encoded_token  # type: ignore [attr-defined]
        ):
            self._log(self._TokenAction.CHECK_KO)
            raise InvalidToken()
        self._log(self._TokenAction.CHECK_OK)

    def expire(self) -> None:
        app.redis_client.delete(Token._get_redis_key(self.type_, self.user_id))  # type: ignore [attr-defined]
        self._log(self._TokenAction.EXPIRE)

    @classmethod
    def load_and_check(cls, encoded_token: str, type_: TokenType, user_id: int | None = None) -> "Token":
        token = Token.load_without_checking(encoded_token)
        token.check(type_, user_id)
        return token

    @classmethod
    def create(cls, type_: TokenType, ttl: timedelta | None, user_id: int, data: dict | None = None) -> "Token":
        encoded_token = utils.encode_jwt_payload({"token_type": type_.value, "user_id": user_id, "data": data})
        app.redis_client.set(cls._get_redis_key(type_, user_id), encoded_token, ex=ttl)  # type: ignore [attr-defined]
        token = Token.load_without_checking(encoded_token)
        token._log(cls._TokenAction.CREATE)
        return token

    @classmethod
    def token_exists(cls, type_: TokenType, user_id: int) -> bool:
        return app.redis_client.exists(cls._get_redis_key(type_, user_id))  # type: ignore [attr-defined]

    def _log(self, action: _TokenAction) -> None:
        logger.info("[TOKEN](%s){%i, %s, %s}", action.value, self.user_id, self.type_.value, self.encoded_token)
