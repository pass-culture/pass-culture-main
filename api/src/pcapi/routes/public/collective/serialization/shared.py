import enum

from pydantic.v1 import validator

from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel


def validate_venue_id(venue_id: int | str | None) -> int | None:
    # TODO(jeremieb): remove this validator once there is no empty
    # string stored as a venueId
    if not venue_id:
        return None
    return int(venue_id)  # should not be needed but it makes mypy happy


class OfferAddressType(enum.Enum):
    OFFERER_VENUE = "offererVenue"
    SCHOOL = "school"
    OTHER = "other"


class OfferVenueModel(BaseModel):
    venueId: int | None
    otherAddress: str | None
    addressType: OfferAddressType

    _validated_venue_id = validator("venueId", pre=True, allow_reuse=True)(validate_venue_id)

    @validator("addressType")
    def validate_address_type(cls, address_type: OfferAddressType, values: dict) -> OfferAddressType:
        venue_id = values.get("venueId")
        other_address = values.get("otherAddress")

        if address_type == OfferAddressType.OFFERER_VENUE and not venue_id:
            raise ValueError(f"venueId est obligatoire avec {address_type.value}")
        if address_type != OfferAddressType.OFFERER_VENUE and venue_id:
            raise ValueError(f"venueId est interdit avec {address_type.value}")

        if address_type == OfferAddressType.OTHER and not other_address:
            raise ValueError(f"otherAddress est obligatoire avec {address_type.value}")
        if address_type != OfferAddressType.OTHER and other_address:
            raise ValueError(f"otherAddress est interdit avec {address_type.value}")

        return address_type

    class Config:
        alias_generator = to_camel
        extra = "forbid"
