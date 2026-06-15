import logging
from datetime import datetime

import jwt

from pcapi import settings


JWT_ADAGE_PUBLIC_KEY_PATH = f"src/pcapi/routes/adage_iframe/public_key/{settings.JWT_ADAGE_PUBLIC_KEY_FILENAME}"


ALGORITHM_HS_256 = "HS256"
ALGORITHM_RS_256 = "RS256"


def encode_jwt_payload(token_payload: dict, expiration_date: datetime | None = None) -> str:
    if expiration_date:
        # do not fill exp key if expiration_date is None or jwt.decode would fail
        token_payload["exp"] = int(expiration_date.timestamp())

    return jwt.encode(
        token_payload,
        settings.JWT_SECRET_KEY,
        algorithm=ALGORITHM_HS_256,
    )


def decode_jwt_token(jwt_token: str) -> dict:
    return jwt.decode(jwt_token, settings.JWT_SECRET_KEY, algorithms=[ALGORITHM_HS_256])


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
