import base64
import binascii
import inspect
import typing

from flask import g

from pcapi.core.geography import models as geography_models
from pcapi.models import api_errors
from pcapi.models import db


class InvalidBase64Exception(Exception):
    pass


def get_address_or_raise_404(address_id: int) -> geography_models.Address:
    address = db.session.query(geography_models.Address).filter(geography_models.Address.id == address_id).one_or_none()

    if not address:
        raise api_errors.ResourceNotFoundError(
            {"location.AddressLocation.addressId": [f"There is no address with id {address_id}"]}
        )
    return address


def get_bytes_from_base64_string(base64_string: str) -> bytes:
    """Return the bytes from a base64 string."""
    try:
        return base64.b64decode(base64_string.encode("utf-8"))
    except binascii.Error as error:
        raise InvalidBase64Exception() from error


def setup_public_api_log_extra(route: typing.Callable) -> None:
    """Setup `public_api_log_request_details_extra` base data

    Add information shared by all public API routes: module, function
    name, api key information; with a `technical_message_id` needed by
    data import tools.

    All these will be added to the base logger under the `extra` key.
    Note that this data can and should be updated (with new keys and
    values) through the whole request's lifecycle. To add any data from
    a controller, for example, call `public_api_add_log_extra`.

    Warning:
        edit the `technical_message_id`'s value with great caution
    """
    if not hasattr(g, "public_api_log_request_details_extra"):
        g.public_api_log_request_details_extra = {}

    raw_module = inspect.getmodule(route)
    module = raw_module.__name__.split(".")[-1] if raw_module is not None else ""

    if hasattr(g, "current_api_key") and g.current_api_key is not None:
        g.public_api_log_request_details_extra["technical_message_id"] = "public_api.call"
        g.public_api_log_request_details_extra["public_api"] = {
            "api_key": g.current_api_key.id,
            "provider_id": g.current_api_key.providerId,
            "module": module,
            "function": route.__name__,
        }


def public_api_add_log_extra(**kwargs: typing.Any) -> None:
    """Entry point for any `public_api_log_request_details_extra` update

    Ensure that every new data update is added at the right place,
    inside the same base object.
    """
    if not hasattr(g, "public_api_log_request_details_extra"):
        # should not be used, but lets be cautious
        g.public_api_log_request_details_extra = {"public_api": {}}
    g.public_api_log_request_details_extra["public_api"].update(kwargs)
