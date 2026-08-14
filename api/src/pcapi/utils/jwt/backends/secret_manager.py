import base64
import json
import logging
from dataclasses import dataclass

import jwt

from pcapi import settings
from pcapi.connectors.google_secret_manager import SecretManagerBackend
from pcapi.connectors.google_secret_manager import SecretManagerException
from pcapi.utils.jwt.backends.base import JwtBaseBackend
from pcapi.utils.redis import get_redis_client


logger = logging.getLogger(__name__)
REDIS_KEY = "pcapi:jwt:JwtSecretManagerBackend:keys"


@dataclass(frozen=True, slots=True)
class CurrentKey:
    key: str  # key used to sign the jwt
    kid: str  # id of the key (timestamp of its creation)


class JwtSecretManagerBackend(JwtBaseBackend):
    _current_key: CurrentKey
    _key_by_kid: dict[str, str]

    def __init__(self) -> None:
        if not settings.JWT_SECRET_KEY:
            raise ValueError("No default jwt key was provided in JWT_SECRET_KEY env variable")

        if not settings.JWT_KEY_SECRET_NAME:
            raise ValueError("No secret name was provided in JWT_KEY_SECRET_NAME env variable")
        self.update_internal_dict()

    def _update_current(self) -> None:
        # will break at the end of year 2286
        kid = max(self._key_by_kid)  # the current key is the one with the most recent timestamp used as kid

        self._current_key = CurrentKey(
            kid=kid if isinstance(kid, str) else kid.decode(),  # helps mypy
            key=self._key_by_kid[kid],
        )

    def _get_key_for_token(self, token: str) -> str:
        split = token.split(".")
        if not len(split) == 3:
            raise jwt.exceptions.InvalidTokenError("jwt %s is not a valid jwt" % token)

        # add padding to make it compatible with b64decode: a base64 string length must be
        # a multiple of 4 and the padding must be done with the symbole '='
        padding = "=" * ((4 - (len(split[0]) % 4)) % 4)

        try:
            raw_headers = base64.b64decode(split[0] + padding)
            headers = json.loads(raw_headers)
        except Exception as exc:
            raise jwt.exceptions.InvalidTokenError("jwt header %s could not be decoded" % split[0]) from exc

        if "kid" not in headers:
            return settings.JWT_SECRET_KEY

        key = self._key_by_kid.get(headers["kid"], "")

        if not key:
            raise jwt.exceptions.InvalidKeyError("jwt header %s has an unknown kid" % split[0])

        return key

    def update_internal_dict(self) -> None:
        # TODO: use a frozendict after update to python 3.15
        key_dict: dict[str, str] = {}
        secret_manager_backend = SecretManagerBackend()

        try:
            secret_generator = secret_manager_backend.get_last_secret_versions(settings.JWT_KEY_SECRET_NAME, limit=60)
            key_dict = {str(s.creation_timestamp): s.value for s in secret_generator}
        except SecretManagerException:
            # something went wrong falling back on redis
            logger.exception("Error while building jwt keyring")
            key_dict = get_redis_client().hgetall(REDIS_KEY)

        if key_dict:
            self._key_by_kid = key_dict
            get_redis_client().hset(REDIS_KEY, mapping=key_dict)  # type: ignore [arg-type]
            self._update_current()
        else:
            raise ValueError("No versions were found for secret %s " % settings.JWT_KEY_SECRET_NAME)

    def encode(self, payload: dict, key: str | None = None) -> str:
        from pcapi.utils.jwt.api import ALGORITHM_HS_256

        headers = {}
        if not key:
            if current := getattr(self, "_current_key", None):
                headers["kid"] = current.kid
                key = current.key
            else:
                # It should not be possible but let's be defensive
                raise ValueError("No key found for signing the jwt")

        self._complete_payload(payload)
        return jwt.encode(
            payload=payload,
            key=key,
            headers=headers,
            algorithm=ALGORITHM_HS_256,
        )

    def decode(self, jwt_token: str, key: str | None = None) -> dict:
        from pcapi.utils.jwt.api import ALGORITHM_HS_256

        key = key if key is not None else self._get_key_for_token(jwt_token)

        return jwt.decode(jwt_token, key, algorithms=[ALGORITHM_HS_256])
