import abc
import dataclasses
from datetime import datetime
from datetime import timedelta
import enum
import json
import logging
import secrets
import typing
import uuid

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


T = typing.TypeVar("T", bound="AbstractToken")


@dataclasses.dataclass(frozen=True)
class AbstractToken(abc.ABC):
    type_: TokenType
    key_suffix: int | str | None
    encoded_token: str
    data: dict

    class _TokenAction(enum.Enum):
        CHECK_OK = "check_ok"
        CHECK_KO = "check_ko"
        EXPIRE = "expire"
        CREATE = "create"

    @classmethod
    def load_and_check(
        cls: typing.Type[T],
        encoded_token: str,
        type_: TokenType,
        user_id: int | None = None,
    ) -> T:
        token = cls.load_without_checking(encoded_token, type_=type_, user_id=user_id)
        token.check(type_, user_id)
        return token

    @classmethod
    def get_redis_key(cls: typing.Type[T], type_: TokenType, key_suffix: int | str | None) -> str:
        return f"pcapi:token:{type_.value}_{key_suffix}"

    @classmethod
    def token_exists(cls: typing.Type[T], type_: TokenType, key_suffix: int | str | None) -> bool:
        return bool(app.redis_client.exists(cls.get_redis_key(type_, key_suffix)))

    @classmethod
    def get_expiration_date(cls: typing.Type[T], type_: TokenType, key_suffix: int | str | None) -> datetime | None:
        key = cls.get_redis_key(type_, key_suffix)
        ttl = app.redis_client.ttl(key)
        if ttl < 0:
            # -2 if doesn't exist, -1 if no expiration
            return None
        return datetime.utcnow() + timedelta(seconds=ttl)

    @classmethod
    def delete(cls: typing.Type[T], type_: TokenType, key_suffix: int | str | None) -> None:
        app.redis_client.delete(cls.get_redis_key(type_, key_suffix))

    @classmethod
    @abc.abstractmethod
    def load_without_checking(cls: typing.Type[T], encoded_token: str, *args: typing.Any, **kwargs: typing.Any) -> T:
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def create(cls: typing.Type[T], type_: TokenType, *args: typing.Any, **kwargs: typing.Any) -> T:
        raise NotImplementedError()

    def get_expiration_date_from_token(self) -> datetime | None:
        return self.get_expiration_date(self.type_, self.key_suffix)

    def check(self, type_: TokenType, key_suffix: int | str | None = None) -> None:
        redis_key = AbstractToken.get_redis_key(self.type_, self.key_suffix)
        if (
            self.type_ != type_
            or (key_suffix is not None and self.key_suffix != key_suffix)
            or app.redis_client.get(redis_key) != self.encoded_token
        ):
            self._log(self._TokenAction.CHECK_KO)
            raise users_exceptions.InvalidToken()
        self._log(self._TokenAction.CHECK_OK)

    def expire(self) -> None:
        app.redis_client.delete(AbstractToken.get_redis_key(self.type_, self.key_suffix))
        self._log(self._TokenAction.EXPIRE)

    def _log(self, action: _TokenAction) -> None:
        logger.info("[TOKEN](%s)%s, %s, %s", action.value, self.key_suffix, self.type_.value, self.encoded_token)


class Token(AbstractToken):
    @property
    def user_id(self) -> int:
        assert self.key_suffix
        return int(self.key_suffix)

    @classmethod
    def load_without_checking(cls, encoded_token: str, *args: typing.Any, **kwargs: typing.Any) -> "Token":
        try:
            payload = utils.decode_jwt_token(encoded_token)
            type_ = TokenType(payload["token_type"])
            user_id = payload["user_id"]
        except jwt.exceptions.ExpiredSignatureError as e:
            raise users_exceptions.ExpiredToken() from e
        except (KeyError, ValueError, jwt.PyJWTError) as e:
            raise users_exceptions.InvalidToken() from e

        data = payload.get("data", {})
        return cls(type_, user_id, encoded_token, data)

    @classmethod
    def create(
        cls,
        type_: TokenType,
        ttl: timedelta | None,
        user_id: int,
        data: dict | None = None,
    ) -> "Token":
        payload: dict[str, typing.Any] = {
            "token_type": type_.value,
            "user_id": user_id,
            "data": data or {},
        }
        if ttl:
            payload["exp"] = (datetime.utcnow() + ttl).timestamp()

        encoded_token = utils.encode_jwt_payload(payload)
        if ttl is None or ttl > timedelta(0):
            app.redis_client.set(cls.get_redis_key(type_, user_id), encoded_token, ex=ttl)
        token = Token.load_without_checking(encoded_token)
        token._log(cls._TokenAction.CREATE)
        return token


@dataclasses.dataclass(frozen=True)
class SixDigitsToken(AbstractToken):
    @classmethod
    def _get_redis_extra_data_key(cls, type_: TokenType, user_id: int) -> str:
        return f"pcapi:token:data:{type_.value}_{user_id}"

    @classmethod
    def load_without_checking(
        cls,
        encoded_token: str,
        type_: TokenType,
        user_id: int,
    ) -> "SixDigitsToken":
        if user_id is None:
            raise ValueError("user_id is required for SixDigitsToken")
        try:
            data_json = app.redis_client.get(cls._get_redis_extra_data_key(type_=type_, user_id=user_id))
            if data_json is None:
                raise users_exceptions.InvalidToken()
            data = json.loads(data_json)
        except json.JSONDecodeError as e:
            raise users_exceptions.InvalidToken() from e
        return cls(type_, user_id, encoded_token, data)

    @classmethod
    def create(
        cls, type_: TokenType, ttl: timedelta | None, user_id: int, data: dict | None = None
    ) -> "SixDigitsToken":
        encoded_token = "{:06}".format(secrets.randbelow(1_000_000))  # 6 digits
        app.redis_client.set(cls.get_redis_key(type_, user_id), encoded_token, ex=ttl)
        json_data = json.dumps(data or {})
        app.redis_client.set(cls._get_redis_extra_data_key(type_, user_id), json_data, ex=ttl)
        token = cls.load_without_checking(encoded_token, type_, user_id)
        token._log(cls._TokenAction.CREATE)
        return token

    @classmethod
    def delete(cls, type_: TokenType, user_id: int | str | None) -> None:
        if not isinstance(user_id, int):
            raise ValueError("user_id can only be an int for SixDigitsToken")
        super().delete(type_, user_id)
        app.redis_client.delete(cls._get_redis_extra_data_key(type_, user_id))

    def expire(self) -> None:
        assert isinstance(self.key_suffix, int), "SixDigitsToken key suffix can only be a user id"
        super().expire()
        app.redis_client.delete(self._get_redis_extra_data_key(self.type_, self.key_suffix))
