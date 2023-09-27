import abc
import dataclasses
from datetime import datetime
from datetime import timedelta
import enum
import json
import logging
import secrets
import typing
from typing import Any
from typing import Type
from typing import TypeVar

from flask import current_app as app
import jwt

from pcapi.core.users import exceptions as users_exceptions
from pcapi.core.users import utils


logger = logging.getLogger(__name__)


class TokenType(enum.Enum):
    EMAIL_CHANGE_CONFIRMATION = "update_email_confirmation"
    EMAIL_CHANGE_VALIDATION = "update_email_validation"
    EMAIL_VALIDATION = "email_validation"
    PHONE_VALIDATION = "phone_validation"
    SUSPENSION_SUSPICIOUS_LOGIN = "suspension_suspicious_login"
    RESET_PASSWORD = "reset_password"


@dataclasses.dataclass(frozen=True)
class AbstractToken(abc.ABC):
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
    @abc.abstractmethod
    def load_without_checking(cls, encoded_token: str, *args: typing.Any, **kwargs: typing.Any) -> "AbstractToken":
        raise NotImplementedError()

    @classmethod
    def load_and_check(
        cls,
        encoded_token: str,
        type_: TokenType,
        user_id: int | None = None,
    ) -> "AbstractToken":
        token = cls.load_without_checking(encoded_token, type_=type_, user_id=user_id)
        token.check(type_, user_id)
        return token

    @classmethod
    @abc.abstractmethod
    def create(cls, type_: TokenType, ttl: timedelta | None, user_id: int, data: dict | None = None) -> "AbstractToken":
        raise NotImplementedError()

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

    def get_expiration_date_from_token(self) -> datetime | None:
        return self.get_expiration_date(self.type_, self.user_id)

    def check(self, type_: TokenType, user_id: int | None = None) -> None:
        redis_key = Token._get_redis_key(self.type_, self.user_id)
        if (
            self.type_ != type_
            or (user_id is not None and self.user_id != user_id)
            or app.redis_client.get(redis_key) != self.encoded_token  # type: ignore [attr-defined]
        ):
            self._log(self._TokenAction.CHECK_KO)
            raise users_exceptions.InvalidToken()
        self._log(self._TokenAction.CHECK_OK)

    def expire(self) -> None:
        app.redis_client.delete(Token._get_redis_key(self.type_, self.user_id))  # type: ignore [attr-defined]
        self._log(self._TokenAction.EXPIRE)

    @classmethod
    def token_exists(cls, type_: TokenType, user_id: int) -> bool:
        return app.redis_client.exists(cls._get_redis_key(type_, user_id))  # type: ignore [attr-defined]

    def _log(self, action: _TokenAction) -> None:
        logger.info("[TOKEN](%s){%i, %s, %s}", action.value, self.user_id, self.type_.value, self.encoded_token)

    @classmethod
    def delete(cls, type_: TokenType, user_id: int) -> None:
        app.redis_client.delete(cls._get_redis_key(type_, user_id))  # type: ignore [attr-defined]

    @classmethod
    def get_token(cls, type_: TokenType, user_id: int) -> "AbstractToken | None":
        raise NotImplementedError()


class Token(AbstractToken):
    @classmethod
    def load_without_checking(cls, encoded_token: str, *args: typing.Any, **kwargs: typing.Any) -> "Token":
        try:
            payload = utils.decode_jwt_token(encoded_token)
        except jwt.exceptions.ExpiredSignatureError:
            raise users_exceptions.ExpiredToken()
        except jwt.PyJWTError:
            raise users_exceptions.InvalidToken()
        try:
            data = payload["data"] if payload["data"] is not None else {}
            type_ = TokenType(payload["token_type"])
            user_id = payload["user_id"]
            return cls(type_, user_id, encoded_token, data)
        except (KeyError, ValueError):
            raise users_exceptions.InvalidToken()

    @classmethod
    def create(cls, type_: TokenType, ttl: timedelta | None, user_id: int, data: dict | None = None) -> "Token":
        payload: dict[str, Any] = {
            "token_type": type_.value,
            "user_id": user_id,
            "data": data,
        }
        if ttl:
            payload["exp"] = (datetime.utcnow() + ttl).timestamp()

        encoded_token = utils.encode_jwt_payload(payload)
        if ttl is None or ttl > timedelta(0):
            app.redis_client.set(cls._get_redis_key(type_, user_id), encoded_token, ex=ttl)  # type: ignore [attr-defined]
        token = Token.load_without_checking(encoded_token)
        token._log(cls._TokenAction.CREATE)
        return token

    @classmethod
    def get_token(cls, type_: TokenType, user_id: int) -> "Token | None":
        encoded_token = app.redis_client.get(cls._get_redis_key(type_, user_id))  # type: ignore [attr-defined]
        if encoded_token is None:
            return None
        return cls.load_without_checking(encoded_token)


@dataclasses.dataclass(frozen=True)
class SixDigitsToken(AbstractToken):
    @classmethod
    def _get_redis_extra_data_key(cls, type_: TokenType, user_id: int) -> str:
        return f"pcapi:token:data:{type_.value}_{user_id}"

    @classmethod
    def load_without_checking(  # type: ignore [override]
        cls,
        encoded_token: str,
        type_: TokenType,
        user_id: int,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> "SixDigitsToken":
        try:
            data_json = app.redis_client.get(cls._get_redis_extra_data_key(type_=type_, user_id=user_id))  # type: ignore [attr-defined]
            if data_json is None:
                raise users_exceptions.InvalidToken()
            data = json.loads(data_json)
        except json.JSONDecodeError:
            raise users_exceptions.InvalidToken()
        return cls(type_, user_id, encoded_token, data)

    @classmethod
    def load_and_check(cls, encoded_token: str, type_: TokenType, user_id: int | None = None) -> "AbstractToken":
        if user_id is None:
            raise ValueError("user_id is required for SixDigitsToken")
        return super().load_and_check(encoded_token, type_, user_id)

    @classmethod
    def create(
        cls, type_: TokenType, ttl: timedelta | None, user_id: int, data: dict | None = None
    ) -> "SixDigitsToken":
        encoded_token = "{:06}".format(secrets.randbelow(1_000_000))  # 6 digits
        app.redis_client.set(cls._get_redis_key(type_, user_id), encoded_token, ex=ttl)  # type: ignore [attr-defined]
        json_data = json.dumps(data or {})
        app.redis_client.set(cls._get_redis_extra_data_key(type_, user_id), json_data, ex=ttl)  # type: ignore [attr-defined]
        token = cls.load_without_checking(encoded_token, type_, user_id)
        token._log(cls._TokenAction.CREATE)
        return token

    def expire(self) -> None:
        super().expire()
        app.redis_client.delete(self._get_redis_extra_data_key(self.type_, self.user_id))  # type: ignore [attr-defined]

    @classmethod
    def delete(cls, type_: TokenType, user_id: int) -> None:
        super().delete(type_, user_id)
        app.redis_client.delete(cls._get_redis_extra_data_key(type_, user_id))  # type: ignore [attr-defined]

    @classmethod
    def get_token(cls, type_: TokenType, user_id: int) -> "SixDigitsToken | None":
        encoded_token = app.redis_client.get(cls._get_redis_key(type_, user_id))  # type: ignore [attr-defined]
        if encoded_token is None:
            return None
        return cls.load_without_checking(encoded_token, type_, user_id)
