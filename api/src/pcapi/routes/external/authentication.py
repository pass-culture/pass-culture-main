import base64
import functools
import hashlib
import hmac
import logging
import typing
from collections.abc import Callable

import ecdsa
import flask
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

from pcapi import settings
from pcapi.connectors.serialization import ubble_serializers
from pcapi.models.api_errors import ForbiddenError
from pcapi.models.api_errors import UnauthorizedError


logger = logging.getLogger(__name__)


def require_dms_token[**P, T](route_function: Callable[P, T]) -> Callable[P, T]:
    @functools.wraps(route_function)
    def validate_dms_token(*args: typing.Any, **kwargs: typing.Any) -> T:
        token = flask.request.args.get("token")
        if not token:
            raise UnauthorizedError()

        if token not in settings.DMS_WEBHOOK_TOKEN_LIST:
            errors = ForbiddenError()
            errors.add_error("token", "Invalid token")
            raise errors

        return route_function(*args, **kwargs)

    return validate_dms_token


def require_ubble_v2_signature[**P, T](route_function: Callable[P, T]) -> Callable[P, T]:
    @functools.wraps(route_function)
    def validate_ubble_signature(*args: typing.Any, **kwargs: typing.Any) -> T:
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
    public_key = typing.cast(
        ec.EllipticCurvePublicKey,
        serialization.load_pem_public_key(raw_public_key.encode("utf-8")),
    )

    try:
        decoded_signature = base64.b64decode(signature.encode("utf-8"))
    except Exception:
        raise ForbiddenError(errors={"signature": ["Invalid signature"]})

    signed_payload = b":".join((timestamp, data))

    try:
        # TODO use as only auth method after 01/01/2027 and remove ecdsa dependancie
        public_key.verify(
            signature=decoded_signature,
            data=signed_payload,
            signature_algorithm=ec.ECDSA(hashes.SHA512()),
        )
        new_signature_check = True
    except InvalidSignature:
        new_signature_check = False
    except Exception:
        logger.exception("An error occured when checking ubble signature with python cryptography")
        new_signature_check = None

    try:
        result = verifying_key.verify(
            decoded_signature,
            signed_payload,
            hashfunc=hashlib.sha512,
            sigdecode=ecdsa.util.sigdecode_der,
            allow_truncate=True,
        )
    except ecdsa.keys.BadSignatureError:
        if new_signature_check:
            logger.error(
                "Ubble signature verification mismatch, please contact @rpaoloni-pass",
                extra={"ecdsa": "error", "pyca/cryptography": "ok"},
            )
        raise ForbiddenError(errors={"signature": ["Invalid signature"]})

    if not result:
        if new_signature_check:
            logger.error(
                "Ubble signature verification mismatch, please contact @rpaoloni-pass",
                extra={"ecdsa": "error", "pyca/cryptography": "ok"},
            )
        raise ForbiddenError(errors={"signature": ["Invalid signature"]})

    if not new_signature_check:
        logger.error(
            "Ubble signature verification mismatch, please contact @rpaoloni-pass",
            extra={"ecdsa": "ok", "pyca/cryptography": "error"},
        )


def require_ubble_signature(route_function: Callable[..., typing.Any]) -> Callable:
    @functools.wraps(route_function)
    def validate_ubble_signature(*args: typing.Any, **kwargs: typing.Any) -> flask.Response:
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


def require_zendesk_webhook_api_key(route_function: Callable[..., typing.Any]) -> Callable:
    @functools.wraps(route_function)
    def validate_zendesk_webhook_api_key(*args: typing.Any, **kwargs: typing.Any) -> flask.Response:
        api_key = flask.request.headers.get("X-Api-Key", "")
        if not api_key:
            raise UnauthorizedError()

        if api_key != settings.ZENDESK_WEBHOOK_API_KEY:
            raise ForbiddenError()

        return route_function(*args, **kwargs)

    return validate_zendesk_webhook_api_key
