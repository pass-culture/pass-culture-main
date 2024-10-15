from pydantic.v1 import ConstrainedFloat
from pydantic.v1 import ConstrainedStr
from pydantic.v1 import root_validator

from pcapi.routes import serialization
from pcapi.routes.public.documentation_constants.fields import fields


class Latitude(ConstrainedFloat):
    le = 90
    ge = -90


class Longitude(ConstrainedFloat):
    le = 180
    ge = -180


class City(ConstrainedStr):
    max_length = 200
    min_length = 1


class Street(ConstrainedStr):
    max_length = 200
    min_length = 1


class PostalCode(ConstrainedStr):
    # First 2 digit are the departement code so should be between 01 and 98
    regex = r"^(?:0[1-9]|[1-8]\d|9[0-8])\d{3}$"


class SearchAddressQuery(serialization.ConfiguredBaseModel):
    street: Street = fields.STREET
    city: City = fields.CITY
    postalCode: PostalCode = fields.POSTAL_CODE
    latitude: Latitude | None = fields.LATITUDE
    longitude: Longitude | None = fields.LONGITUDE

    @root_validator(skip_on_failure=True)
    def check_lat_long_and_banId_are_correctly_set(cls, values: dict) -> dict:
        latitude = values.get("latitude")
        longitude = values.get("longitude")

        # Ensure both latitude and longitude are either both set or both null
        if latitude is not None and longitude is None:
            raise ValueError("`longitude` must be set if `latitude` is provided")
        if latitude is None and longitude is not None:
            raise ValueError("`latitude` must be set if `longitude` is provided")

        return values


class GetAddressResponse(serialization.ConfiguredBaseModel):
    id: int
    latitude: float = fields.LATITUDE
    longitude: float = fields.LONGITUDE
    banId: str | None = fields.BAN_ID
    city: str | None = fields.CITY
    postalCode: str | None = fields.POSTAL_CODE
    street: str | None = fields.STREET


class SearchAddressResponse(serialization.ConfiguredBaseModel):
    addresses: list[GetAddressResponse]
