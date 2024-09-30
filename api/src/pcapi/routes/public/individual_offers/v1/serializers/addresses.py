from pydantic.v1 import ConstrainedFloat
from pydantic.v1 import root_validator

from pcapi.routes import serialization
from pcapi.routes.public.documentation_constants.fields import fields


class Latitude(ConstrainedFloat):
    le = 90
    ge = -90


class Longitude(ConstrainedFloat):
    le = 180
    ge = -180


class GetAddressQuery(serialization.ConfiguredBaseModel):
    latitude: Latitude | None = fields.LATITUDE
    longitude: Longitude | None = fields.LONGITUDE
    banId: str | None = fields.BAN_ID

    @root_validator(skip_on_failure=True)
    def check_lat_long_and_banId_are_correctly_set(cls, values: dict) -> dict:
        latitude = values.get("latitude")
        longitude = values.get("longitude")
        ban_id = values.get("banId")

        # Ensure both latitude and longitude are either both set or both null
        if latitude is not None and longitude is None:
            raise ValueError("`longitude` must be set if `latitude` is provided")
        if latitude is None and longitude is not None:
            raise ValueError("`latitude` must be set if `longitude` is provided")

        # both banId and lat/long set
        if ban_id is not None and latitude is not None:
            raise ValueError(
                "`latitude/longitude` and `banId` cannot be both set. Use either `latitude/longitude` or `banId`"
            )

        # both banId and lat/long null
        if ban_id is None and latitude is None:
            raise ValueError("Either `latitude/longitude` or `banId` must be set")

        return values


class GetAddressResponse(serialization.ConfiguredBaseModel):
    latitude: float = fields.LATITUDE
    longitude: float = fields.LONGITUDE
    banId: str | None = fields.BAN_ID
    city: str | None = fields.CITY
    postalCode: str | None = fields.POSTAL_CODE
    street: str | None = fields.STREET
