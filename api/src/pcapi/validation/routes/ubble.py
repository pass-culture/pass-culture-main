import functools
import hashlib
import hmac
from typing import Any
from typing import Callable

import flask

from pcapi import settings
from pcapi.connectors.serialization import ubble_serializers
from pcapi.models.api_errors import ForbiddenError


def require_ubble_signature(route_function: Callable[..., Any]) -> Callable:
    @functools.wraps(route_function)
    def validate_ubble_signature(*args: Any, **kwargs: Any) -> flask.Response:
        error = ForbiddenError(errors={"signature": ["Invalid signature"]})
        signature = getattr(
            ubble_serializers.UBBLE_SIGNATURE_RE.match(flask.request.headers.get("Ubble-Signature", "")),
            "groupdict",
            lambda: None,
        )()
        if not (signature and signature.get("ts") and signature.get("v1")):
            raise error

        expected_signature = compute_signature(signature["ts"].encode("utf-8"), flask.request.data)
        if signature["v1"] != expected_signature:
            raise error

        return route_function(*args, **kwargs)

    return validate_ubble_signature


def compute_signature(ts: bytes, payload: bytes) -> str:
    webhook_secret: str = settings.UBBLE_WEBHOOK_SECRET
    assert webhook_secret is not None
    signed_payload = b".".join((ts, payload))
    signature = hmac.new(
        settings.UBBLE_WEBHOOK_SECRET.encode("utf-8"),
        msg=signed_payload,
        digestmod=hashlib.sha256,
    ).hexdigest()
    return signature
