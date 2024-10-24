import functools
import hashlib
import hmac
import re
from typing import Any
from typing import Callable

import flask
import pydantic.v1 as pydantic_v1

from pcapi import settings
from pcapi.connectors.serialization import ubble_serializers
from pcapi.models.api_errors import ForbiddenError


UBBLE_SIGNATURE_RE = re.compile(r"^ts=(?P<ts>\d+),v1=(?P<v1>\S{64})$")


# TODO move this file to serialization
class Configuration(pydantic_v1.BaseModel):
    id: int
    name: str


class WebhookRequest(pydantic_v1.BaseModel):
    identification_id: str
    status: ubble_serializers.UbbleIdentificationStatus
    configuration: Configuration


class WebhookRequestHeaders(pydantic_v1.BaseModel):
    ubble_signature: str = pydantic_v1.Field(..., regex=UBBLE_SIGNATURE_RE.pattern, alias="Ubble-Signature")

    class Config:
        extra = "allow"


# Ubble only consider HTTP status 200 and 201 as success
# but we are not able to respond with empty body unless we return a 204 HTTP status
# so we need a dummy reponse_model to be used for the webhook response
class WebhookDummyReponse(pydantic_v1.BaseModel):
    status: str = "ok"


class WebhookStoreIdPicturesRequest(pydantic_v1.BaseModel):
    identification_id: str


def require_ubble_signature(route_function: Callable[..., Any]) -> Callable:
    @functools.wraps(route_function)
    def validate_ubble_signature(*args: Any, **kwargs: Any) -> flask.Response:
        error = ForbiddenError(errors={"signature": ["Invalid signature"]})
        signature = getattr(
            UBBLE_SIGNATURE_RE.match(flask.request.headers.get("Ubble-Signature", "")),
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
