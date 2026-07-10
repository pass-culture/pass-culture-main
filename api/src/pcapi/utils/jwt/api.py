import typing
from datetime import datetime

import jwt
from flask import current_app

from pcapi import settings
from pcapi.utils.jwt.backends.simple import JwtSimpleBackend


if typing.TYPE_CHECKING:
    from flask import Flask

    from pcapi.utils.jwt.backends.base import JwtBaseBackend


JWT_ADAGE_PUBLIC_KEY_PATH = f"src/pcapi/routes/adage_iframe/public_key/{settings.JWT_ADAGE_PUBLIC_KEY_FILENAME}"
ALGORITHM_HS_256 = "HS256"
ALGORITHM_RS_256 = "RS256"
_JWT_BACKEND_ATTR = "pc_jwt_backend"
_BACKEND_CLASSES = {
    "JwtSimpleBackend": JwtSimpleBackend,
}


def setup_backend(app: "Flask") -> None:
    if not hasattr(app, _JWT_BACKEND_ATTR):
        try:
            backend_class = _BACKEND_CLASSES[settings.JWT_BACKEND]
        except KeyError:
            raise ValueError("JWT backend %s not found." % settings.JWT_BACKEND)
        setattr(app, _JWT_BACKEND_ATTR, backend_class())


def get_backend() -> "JwtBaseBackend":
    jwt_backend = getattr(current_app, _JWT_BACKEND_ATTR, None)
    if jwt_backend is None:
        raise RuntimeError("get_backend should not be called before setup_backend.")
    return jwt_backend


def encode_jwt_payload(token_payload: dict, expiration_date: datetime | None = None) -> str:
    if expiration_date:
        # do not fill exp key if expiration_date is None or jwt.decode would fail
        token_payload["exp"] = int(expiration_date.timestamp())
    return get_backend().encode(payload=token_payload)


def decode_jwt_token(jwt_token: str) -> dict:
    return get_backend().decode(jwt_token=jwt_token)


def encode_jwt_payload_rs256(
    token_payload: dict,
    private_key: str | bytes,
    expiration_date: datetime | None = None,
) -> str:
    if expiration_date:
        # do not fill exp key if expiration_date is None or jwt.decode would fail
        token_payload["exp"] = int(expiration_date.timestamp())
    return jwt.encode(token_payload, key=private_key, algorithm=ALGORITHM_RS_256)


def decode_jwt_token_rs256(
    jwt_token: str, public_key: str | bytes | None = None, verify_signature: bool = True, require: list | None = None
) -> dict:
    if (not public_key and verify_signature) or (public_key and not verify_signature):
        raise RuntimeError(
            "You have to either provide the public_key to verify the signature or the use the `verify_signature` options set to False"
        )
    options = jwt.types.Options({"verify_signature": verify_signature, "require": require or []})
    if public_key:
        return jwt.decode(jwt_token, key=public_key, algorithms=[ALGORITHM_RS_256], options=options)
    return jwt.decode(jwt_token, algorithms=[ALGORITHM_RS_256], options=options)
