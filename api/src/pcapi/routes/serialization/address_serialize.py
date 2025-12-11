import typing

import pydantic.v1 as pydantic_v1
from pydantic.v1 import validator

from pcapi.core.offerers import schemas as offerers_schema
from pcapi.core.offerers.models import OffererAddress
from pcapi.routes.serialization import BaseModel


# Legacy (pydantic V1)
class LocationOnlyOnVenueBodyModel(BaseModel):
    isVenueLocation: bool

    @validator("isVenueLocation")
    def validate_is_venue_location(cls, is_venue_location: bool) -> bool:
        if is_venue_location is not True:
            raise ValueError()
        return is_venue_location


class LocationBodyModel(offerers_schema.LocationModel):
    isVenueLocation: bool = False

    @validator("isVenueLocation")
    def validate_is_venue_location(cls, is_venue_location: bool) -> bool:
        if is_venue_location is False:
            return is_venue_location
        raise ValueError("isVenueLocation must be false when providing a full address")


class LocationResponseModel(BaseModel):
    id: int
    label: str | None = None
    isManualEdition: bool
    isVenueLocation: bool
    banId: str | None
    inseeCode: str | None
    postalCode: str
    street: str | None
    city: str
    latitude: float
    longitude: float
    departmentCode: str | None

    class Config:
        orm_mode = True

    @pydantic_v1.validator("latitude", "longitude")
    def round(cls, value: float) -> float:
        """Rounding to five digits to keep consistency
        with the model definition.
        """
        return round(value, 5)


class VenueAddressInfoGetter(pydantic_v1.utils.GetterDict):
    def get(self, key: str, default: typing.Any = None) -> typing.Any:
        venue = self._obj
        if key == "coordinates":
            return {
                "latitude": venue.offererAddress.address.latitude,
                "longitude": venue.offererAddress.address.longitude,
            }
        if key == "address" or key == "street":
            return venue.offererAddress.address.street
        if key == "city":
            return venue.offererAddress.address.city
        if key == "postalCode":
            return venue.offererAddress.address.postalCode
        if key == "departmentCode" or key == "departementCode":
            return venue.offererAddress.address.departmentCode

        return super().get(key, default)


def retrieve_address_info_from_oa(offerer_address: OffererAddress) -> dict:
    """Utility function that retrieves the location information from the offerer_address"""
    return dict(
        id=offerer_address.addressId,
        id_oa=offerer_address.id,
        banId=offerer_address.address.banId,
        inseeCode=offerer_address.address.inseeCode,
        postalCode=offerer_address.address.postalCode,
        street=offerer_address.address.street,
        departmentCode=offerer_address.address.departmentCode,
        city=offerer_address.address.city,
        longitude=offerer_address.address.longitude,
        latitude=offerer_address.address.latitude,
        isManualEdition=offerer_address.address.isManualEdition,
    )
