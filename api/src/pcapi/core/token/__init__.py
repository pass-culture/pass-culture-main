import abc
import dataclasses
from datetime import datetime
from datetime import timedelta
import enum
import json
import logging
import random
import secrets
import time
import typing
import uuid

from flask import current_app as app
import jwt

from pcapi import settings
from pcapi.core.users import exceptions as users_exceptions
from pcapi.core.users import utils


logger = logging.getLogger(__name__)


class TokenType(enum.Enum):
    EMAIL_CHANGE_CONFIRMATION = "update_email_confirmation"
    EMAIL_CHANGE_NEW_EMAIL_SELECTION = "update_email_new_mail_selection"
    EMAIL_CHANGE_VALIDATION = "update_email_validation"
    EMAIL_VALIDATION = "email_validation"
    PHONE_VALIDATION = "phone_validation"
    SUSPENSION_SUSPICIOUS_LOGIN = "suspension_suspicious_login"
    RESET_PASSWORD = "reset_password"
    RECENTLY_RESET_PASSWORD = "recently_reset_password"
    ACCOUNT_CREATION = "account_creation"
    OAUTH_STATE = "oauth_state"
    DISCORD_OAUTH = "discord_oauth"


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
    def get_token(cls: typing.Type[T], type_: TokenType, key_suffix: int | str | None) -> "T | None":
        encoded_token = app.redis_client.get(cls.get_redis_key(type_, key_suffix))
        if encoded_token is None:
            return None
        return cls.load_without_checking(encoded_token)

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


class UUIDToken(AbstractToken):
    @classmethod
    def load_and_check(
        cls,
        encoded_token: str,
        type_: TokenType,
        key_suffix: int | str | None = None,
    ) -> "UUIDToken":
        token = cls.load_without_checking(encoded_token)
        token.check(type_, token.key_suffix)
        return token

    @classmethod
    def load_without_checking(
        cls,
        encoded_token: str,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> "UUIDToken":
        try:
            payload = utils.decode_jwt_token(encoded_token)
        except jwt.exceptions.ExpiredSignatureError as e:
            raise users_exceptions.ExpiredToken() from e
        except (KeyError, ValueError, jwt.PyJWTError) as e:
            raise users_exceptions.InvalidToken() from e

        data = payload.get("data", {})
        type_ = TokenType(payload["token_type"])
        uuid4 = payload["uuid"]
        return cls(type_, uuid4, encoded_token, data)

    @classmethod
    def create(cls, type_: TokenType, ttl: timedelta | None, data: dict | None = None) -> "UUIDToken":
        random_uuid = str(uuid.uuid4())
        payload: dict[str, typing.Any] = {
            "token_type": type_.value,
            "uuid": random_uuid,
            "data": data or {},
        }
        if ttl:
            payload["exp"] = (datetime.utcnow() + ttl).timestamp()
        encoded_token = utils.encode_jwt_payload(payload)

        if ttl is None or ttl > timedelta(0):
            redis_key = cls.get_redis_key(type_, random_uuid)
            app.redis_client.set(redis_key, encoded_token, ex=ttl)

        token = UUIDToken.load_without_checking(encoded_token)
        token._log(cls._TokenAction.CREATE)
        return token


class SecureToken:
    """A "single use token" implementation that put emphasis on security over any other concerns"""

    def __init__(self, token: str = "", ttl: int = 30, data: dict | None = None):
        """
        This object has two modes:
        - If token is provided this class will try to retrieve the data from redis. If they are not found it will
        raise a ValueError. Warning retrieving a token from redis will destroy it (it is single use and this
        operation is atomic)
        - If no token is provided this class will dump data in json, generate a token and store the data with the
        ttl (in seconds) in redis.

        Once the object has been instantiated you can retrieve the data with token.data and the token with
        token.token.
        """
        if token:
            self.token = token
            # # TODO replace get+delete by getdel once we have access to a redis 6.2+
            # raw_data = app.redis_client.getdel(self.key)
            with app.redis_client.pipeline(transaction=True) as pipeline:
                pipeline.get(self.key)
                pipeline.delete(self.key)
                results = pipeline.execute()
            raw_data = results[0]
            if not raw_data:
                # add robustness against timing attacks
                time.sleep(random.random())
                raise users_exceptions.InvalidToken()
            self.data = json.loads(raw_data)
        else:
            self.data = data or {}
            # generate a 512 bits secure token
            self.token = secrets.token_urlsafe(64)
            raw_data = json.dumps(self.data)
            app.redis_client.set(self.key, raw_data, ex=ttl)

    @property
    def key(self) -> str:
        return f"pcapi:token:SecureToken_{self.token}"


class AsymetricToken(AbstractToken):
    """A token that uses asymmetric encryption to encode and decode the token
    mainly used for external services that need to verify the token signature
    """

    @classmethod
    def load_without_checking(
        cls, encoded_token: str, public_key: str, *args: typing.Any, **kwargs: typing.Any
    ) -> "AsymetricToken":
        try:
            payload = utils.decode_jwt_token_rs256(
                encoded_token, public_key=public_key
            )  # do we want to use the same key to all our tokens?
            type_ = TokenType(payload["token_type"])
            uuid4 = payload["uuid"]
        except jwt.exceptions.ExpiredSignatureError as e:
            raise users_exceptions.ExpiredToken() from e
        except (KeyError, ValueError, jwt.PyJWTError) as e:
            raise users_exceptions.InvalidToken() from e

        data = payload.get("data", {})
        return cls(type_, uuid4, encoded_token, data)

    @classmethod
    def create(
        cls,
        type_: TokenType,
        private_key: str,
        public_key: str,
        ttl: timedelta | None,
        data: dict | None = None,
    ) -> "AsymetricToken":
        random_uuid = str(uuid.uuid4())
        payload: dict[str, typing.Any] = {
            "token_type": type_.value,
            "uuid": random_uuid,
            "data": data or {},
        }
        if ttl:
            payload["exp"] = (datetime.utcnow() + ttl).timestamp()

        encoded_token = utils.encode_jwt_payload_rs256(payload, private_key=private_key)
        if ttl is None or ttl > timedelta(0):
            app.redis_client.set(cls.get_redis_key(type_, random_uuid), encoded_token, ex=ttl)
        token = cls.load_without_checking(encoded_token, public_key=public_key)
        token._log(cls._TokenAction.CREATE)
        return token
