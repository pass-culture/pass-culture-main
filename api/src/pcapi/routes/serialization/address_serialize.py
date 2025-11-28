import typing
from decimal import Decimal
from decimal import InvalidOperation

import pydantic.v1 as pydantic_v1
from pydantic.v1 import validator

from pcapi.core.offerers import schemas as offerers_schema
from pcapi.core.offerers.models import OffererAddress
from pcapi.routes.serialization import BaseModel


class AddressResponseModel(BaseModel):
    id: int
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


class LocationOnlyOnVenueBodyModel(BaseModel):
    venueLocation: bool

    @validator("venueLocation")
    def validate_venue_location(cls, venue_location: bool) -> bool:
        if venue_location is not True:
            raise ValueError()
        return venue_location


class LocationBodyModel(BaseModel):
    label: str | None = None
    venueLocation: bool = False
    isManualEdition: bool = False
    banId: str | None
    inseeCode: str | None
    postalCode: str
    street: str
    city: str
    latitude: float | str
    longitude: float | str
    departmentCode: str | None

    class Config:
        orm_mode = True

    @validator("venueLocation")
    def validate_venue_location(cls, venue_location: bool) -> bool:
        if venue_location is False:
            return venue_location
        raise ValueError("venueLocation must be false when providing a full address")

    @validator("city")
    def title_city_when_manually_edited(cls, city: str, values: dict) -> str:
        if values["isManualEdition"] is True:
            return city.title()
        return city

    @validator("latitude", pre=True)
    @classmethod
    def validate_latitude(cls, raw_latitude: str, values: dict) -> str:
        try:
            latitude = Decimal(raw_latitude)
        except InvalidOperation:
            raise ValueError("Format incorrect")
        if not -offerers_schema.MAX_LATITUDE < latitude < offerers_schema.MAX_LATITUDE:
            raise ValueError(
                f"La latitude doit être comprise entre -{offerers_schema.MAX_LATITUDE} et +{offerers_schema.MAX_LATITUDE}"
            )
        return raw_latitude

    @validator("longitude", pre=True)
    @classmethod
    def validate_longitude(cls, raw_longitude: str, values: dict) -> str:
        try:
            longitude = Decimal(raw_longitude)
        except InvalidOperation:
            raise ValueError("Format incorrect")
        if not -offerers_schema.MAX_LONGITUDE < longitude < offerers_schema.MAX_LONGITUDE:
            raise ValueError(
                f"La longitude doit être comprise entre -{offerers_schema.MAX_LONGITUDE} et +{offerers_schema.MAX_LONGITUDE}"
            )
        return raw_longitude


class LocationResponseModel(BaseModel):
    id: int
    label: str | None = None
    venueLocation: bool
    isManualEdition: bool
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
