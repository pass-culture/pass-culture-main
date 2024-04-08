import base64
import functools
import hashlib
import hmac
from typing import Any
from typing import Callable

import ecdsa
import flask

from pcapi import settings
from pcapi.connectors.serialization import ubble_serializers
from pcapi.models.api_errors import ForbiddenError
from pcapi.models.api_errors import UnauthorizedError


def require_ubble_v2_signature(route_function: Callable[..., Any]) -> Callable:
    @functools.wraps(route_function)
    def validate_ubble_signature(*args: Any, **kwargs: Any) -> flask.Response:
        signature = flask.request.headers.get("Cko-Signature", "")
        if not signature:
            raise UnauthorizedError(errors={"signature": ["Missing signature"]})

        try:
            (timestamp, _ubble_signature_version, ubble_signature) = signature.split(":")
        except ValueError as e:
            raise ForbiddenError(errors={"signature": ["Invalid signature structure"]}) from e

        check_v2_signature(timestamp.encode("utf-8"), flask.request.data, ubble_signature)

        return route_function(*args, **kwargs)

    return validate_ubble_signature


def check_v2_signature(timestamp: bytes, data: bytes, signature: str) -> None:
    """
    Inspired by Ubble's documentation:
    https://github.com/ubbleai/code-samples/blob/main/signature_validation/python/check_webhook_signature.py
    """
    with open(settings.UBBLE_SIGNATURE_KEY_PATH, encoding="utf-8") as ubble_signature_file:
        raw_public_key = ubble_signature_file.read()
    verifying_key = ecdsa.VerifyingKey.from_pem(raw_public_key)

    try:
        decoded_signature = base64.b64decode(signature.encode("utf-8"))
    except Exception:
        raise ForbiddenError(errors={"signature": ["Invalid signature"]})

    signed_payload = b":".join((timestamp, data))
    try:
        result = verifying_key.verify(
            decoded_signature,
            signed_payload,
            hashfunc=hashlib.sha512,
            sigdecode=ecdsa.util.sigdecode_der,
            allow_truncate=True,
        )
    except ecdsa.keys.BadSignatureError:
        raise ForbiddenError(errors={"signature": ["Invalid signature"]})

    if not result:
        raise ForbiddenError(errors={"signature": ["Invalid signature"]})


def require_ubble_signature(route_function: Callable[..., Any]) -> Callable:
    @functools.wraps(route_function)
    def validate_ubble_signature(*args: Any, **kwargs: Any) -> flask.Response:
        error = ForbiddenError(errors={"signature": ["Invalid signature"]})
        raw_signature = flask.request.headers.get("Ubble-Signature", "")
        if not raw_signature:
            raise UnauthorizedError()

        signature = ubble_serializers.UBBLE_SIGNATURE_RE.match(raw_signature)
        if not signature:
            raise error

        credentials = signature.groupdict()
        if not credentials.get("ts") or not credentials.get("v1"):
            raise error

        expected_signature = compute_signature(credentials["ts"].encode("utf-8"), flask.request.data)
        if credentials["v1"] != expected_signature:
            raise error

        return route_function(*args, **kwargs)

    return validate_ubble_signature


def compute_signature(ts: bytes, payload: bytes) -> str:
    """
    Inspired by Ubble's documentation:
    https://ubbleai.github.io/developer-documentation/?python#webhook
    """
    webhook_secret: str = settings.UBBLE_WEBHOOK_SECRET
    assert webhook_secret is not None
    signed_payload = b".".join((ts, payload))
    signature = hmac.new(
        settings.UBBLE_WEBHOOK_SECRET.encode("utf-8"),
        msg=signed_payload,
        digestmod=hashlib.sha256,
    ).hexdigest()
    return signature
