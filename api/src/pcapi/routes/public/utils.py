import base64
import binascii

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
