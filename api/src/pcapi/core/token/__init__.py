import abc
import dataclasses
import enum
import hashlib
import json
import logging
import random
import secrets
import time
import typing
import uuid
from datetime import datetime
from datetime import timedelta

import jwt
from flask import current_app as app

from pcapi import settings
from pcapi.core.users import exceptions as users_exceptions
from pcapi.core.users import utils


logger = logging.getLogger(__name__)


class TokenType(enum.Enum):
    EMAIL_CHANGE_CONFIRMATION = "update_email_confirmation"
    EMAIL_CHANGE_NEW_EMAIL_SELECTION = "update_email_new_mail_selection"
    EMAIL_CHANGE_VALIDATION = "update_email_validation"
    SIGNUP_EMAIL_CONFIRMATION = "email_validation"
    PHONE_VALIDATION = "phone_validation"
    SUSPENSION_SUSPICIOUS_LOGIN = "suspension_suspicious_login"
    RESET_PASSWORD = "reset_password"
    RECENTLY_RESET_PASSWORD = "recently_reset_password"
    ACCOUNT_CREATION = "account_creation"
    OAUTH_STATE = "oauth_state"
    DISCORD_OAUTH = "discord_oauth"
    PASSWORDLESS_LOGIN = "passwordless_login"


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
    def load_and_check(cls: typing.Type[T], encoded_token: str, *args: typing.Any, **kwargs: typing.Any) -> T:
        token = cls.load_without_checking(encoded_token, *args, **kwargs)
        token.check(*args, **kwargs)
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
    def load_and_check(
        cls, encoded_token: str, public_key: bytes, *args: typing.Any, **kwargs: typing.Any
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
    def load_without_checking(cls, encoded_token: str, *args: typing.Any, **kwargs: typing.Any) -> "AsymetricToken":
        """Decode the JWT token without verifying signature. If you want to be able to trust
        the data within the payload, you must use `load_and_check`
        """
        payload = utils.decode_jwt_token_rs256(encoded_token, verify_signature=False)
        type_ = TokenType(payload["token_type"])
        uuid4 = payload["uuid"]

        data = payload.get("data", {})
        return cls(type_, uuid4, encoded_token, data)

    @classmethod
    def create(
        cls,
        type_: TokenType,
        private_key: bytes,
        ttl: timedelta | None,
        *,
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
        token = cls(type_, random_uuid, encoded_token, payload["data"])
        token._log(cls._TokenAction.CREATE)
        return token


PASSWORDLESS_REDIS_KEY_TEMPLATE = "pcapi:token:%(type_)s:%(key_suffix)s"


def create_passwordless_login_token(user_id: int, ttl: timedelta) -> str:
    """
    Single use token that allow a user to login without entering any credentials.
    This token is signed using a RSA private key and verified using the corresponding
    public key.
    In exchange of this token, a user should be returned a valid session.

    The payload of this token expects several claims:

        jti: Token unique identifier preventing replay attacks. Ensure each JWT is used only once.
        sub: The subject of the token. Contains the user id.
        iat: Issued at.
        exp: Expiration date.

    Returns:
        A JWT token (str)
    """
    issued_at = datetime.utcnow()
    expiration_date = issued_at + ttl

    jti = str(uuid.uuid4())
    exp = int(expiration_date.timestamp())
    iat = int(issued_at.timestamp())
    sub = str(user_id)

    # There's virtually none chance two users can have the same
    # jti within the lifetime of their respective token.
    # However let's be defensive, hashing together the user_id and the corresponding jti
    # we ensure this case is covered.
    value = json.dumps({"user_id": sub, "jti": jti})
    key_suffix = hashlib.sha256(value.encode()).hexdigest()
    redis_key = PASSWORDLESS_REDIS_KEY_TEMPLATE % {
        "type_": TokenType.PASSWORDLESS_LOGIN.value,
        "key_suffix": key_suffix,
    }
    app.redis_client.set(redis_key, value, ex=ttl)

    token = utils.encode_jwt_payload_rs256(
        {"sub": sub, "iat": iat, "exp": exp, "jti": jti},
        private_key=settings.PASSWORDLESS_LOGIN_PRIVATE_KEY,
        expiration_date=expiration_date,
    )
    return token


def validate_passwordless_token(token: str) -> dict:
    """Validate and consume the passwordless login token.
    If valid, return the content of the payload.

    Returns:
        payload (dict): The payload of the token containing the JTI, the subject (user_id), the expiration and issued_at dates.

    Raises:
        InvalidToken (exception): If anything goes wrong while decoding or validating the token, we don’t want to give any additional hints, we raise `InvalidToken` in any cases.
    """
    try:
        payload = utils.decode_jwt_token_rs256(
            token, public_key=settings.PASSWORDLESS_LOGIN_PUBLIC_KEY, require=["exp", "iat", "sub", "jti"]
        )
    except jwt.ExpiredSignatureError as exc:
        # Authentic but expired token
        raise users_exceptions.ExpiredToken() from exc
    except jwt.InvalidAlgorithmError as exc:
        # Not a JWT token because wrong algo
        raise exc
    except jwt.PyJWTError as exc:
        # Base exception for all others case we might be interested on
        logger.warning(
            "%s (reason: %s) raised while decoding passwordless login token: %s", exc.__class__.__name__, exc, token
        )
        raise users_exceptions.InvalidToken from exc

    value = json.dumps({"user_id": payload["sub"], "jti": payload["jti"]})
    key_suffix = hashlib.sha256(value.encode()).hexdigest()
    redis_key = PASSWORDLESS_REDIS_KEY_TEMPLATE % {
        "type_": TokenType.PASSWORDLESS_LOGIN.value,
        "key_suffix": key_suffix,
    }

    with app.redis_client.pipeline() as pipeline:
        pipeline.get(redis_key)
        pipeline.delete(redis_key)
        results = pipeline.execute()

    if not results[0]:
        logger.error("Token doesn’t exist or was already used.")
        raise users_exceptions.InvalidToken
    redis_value = json.loads(results[0])
    # The below statement are purely defensive code.
    # We should ALWAYS have a perfect match between
    # the payload of the token and what has been stored in the redis queue
    if redis_value["user_id"] != payload["sub"] or redis_value["jti"] != payload["jti"]:
        # Aborting
        logger.error(
            "Mismatch between the payload of an authentic passwordless login token and the corresponding redis value. Token: %s",
            token,
        )
        raise users_exceptions.InvalidToken

    return payload
