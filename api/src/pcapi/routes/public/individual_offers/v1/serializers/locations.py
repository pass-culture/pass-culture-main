import typing

import pydantic as pydantic_v2
from typing_extensions import Annotated

from pcapi.core.offers import models as offers_models
from pcapi.routes.public.documentation_constants.fields_v2 import fields_v2
from pcapi.routes.serialization import HttpBodyModel


AddressLabel = Annotated[str, pydantic_v2.Field(min_length=1, max_length=100)]


class AddressLocationV2(HttpBodyModel):
    """
    If your offer location is different from the venue location
    """

    type: typing.Literal["address"] = "address"
    venue_id: int = fields_v2.VENUE_ID
    address_id: int = fields_v2.ADDRESS_ID
    address_label: AddressLabel | None = fields_v2.ADDRESS_LABEL_NOT_REQUIRED

    @classmethod
    def build_from_offer(cls, offer: offers_models.Offer) -> "AddressLocationV2":
        if not offer.offererAddress:
            raise ValueError("offer.offererAddress is `None`")

        if offer.offererAddress.addressId is None:
            raise ValueError("offer.offererAddress.addressId is `None`")

        return cls(
            type="address",
            venue_id=offer.venueId,
            address_id=offer.offererAddress.addressId,
            address_label=offer.offererAddress.label,
        )


class PhysicalLocationV2(HttpBodyModel):
    """
    If your offer location is your venue
    """

    type: typing.Literal["physical"] = "physical"
    venue_id: int = fields_v2.VENUE_ID


class DigitalLocationV2(HttpBodyModel):
    """
    If your offer has no physical location as it is a digital product
    """

    type: typing.Literal["digital"] = "digital"
    venue_id: int = fields_v2.VENUE_ID
    url: pydantic_v2.HttpUrl = fields_v2.DIGITAL_LOCATION_URL
