import base64
import binascii
import typing

from flask import g
from flask import request

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

    Add information shared by all public API routes: api key id and provider id.

    All these will be added to the base logger under the `extra` key.
    Note that this data can and should be updated (with new keys and
    values) through the whole request's lifecycle. To add any data from
    a controller, for example, call `public_api_add_log_extra`.
    """
    if not hasattr(g, "public_api_log_request_details_extra"):
        g.public_api_log_request_details_extra = {}

    if hasattr(g, "current_api_key") and g.current_api_key is not None:
        g.public_api_log_request_details_extra["api_key_id"] = g.current_api_key.id
        g.public_api_log_request_details_extra["provider_id"] = g.current_api_key.providerId

        if request.path.startswith("/public/offers/v1") and request.is_json:
            venue_id = (request.json.get("location", {}) or {}).get("venueId", None)
            if venue_id is not None:
                g.public_api_log_request_details_extra["venue_id"] = venue_id


def public_api_add_log_extra(**kwargs: typing.Any) -> None:
    """Entry point for any `public_api_log_request_details_extra` update

    Ensure that every new data update is added at the right place,
    inside the same base object.
    """
    if not hasattr(g, "public_api_log_request_details_extra"):
        # should not be used, but lets be cautious
        g.public_api_log_request_details_extra = {}
    g.public_api_log_request_details_extra.update(kwargs)
