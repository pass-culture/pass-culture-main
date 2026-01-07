import pydantic as pydantic_v2
from typing_extensions import Annotated

from pcapi.routes import serialization
from pcapi.routes.public.documentation_constants.fields_v2 import fields_v2


Street = Annotated[str, pydantic_v2.Field(max_length=200, min_length=1)]
City = Annotated[str, pydantic_v2.Field(max_length=200, min_length=1)]
PostalCode = Annotated[str, pydantic_v2.Field(pattern=r"^(?:0[1-9]|[1-8]\d|9[0-8])\d{3}$")]
Latitude = Annotated[float, pydantic_v2.Field(le=90, ge=-90)]
Longitude = Annotated[float, pydantic_v2.Field(le=180, ge=-180)]


class AddressModel(serialization.HttpBodyModel):
    street: Street = fields_v2.STREET
    city: City = fields_v2.CITY
    postalCode: PostalCode = fields_v2.POSTAL_CODE
    latitude: Latitude | None = fields_v2.LATITUDE_NOT_REQUIRED
    longitude: Longitude | None = fields_v2.LONGITUDE_NOT_REQUIRED

    @pydantic_v2.model_validator(mode="after")
    def check_lat_long_and_banId_are_correctly_set(self) -> "AddressModel":
        latitude = self.latitude
        longitude = self.longitude

        # Ensure both latitude and longitude are either both set or both null
        if latitude is not None and longitude is None:
            self._raise(self.longitude, "longitude", "`longitude` must be set if `latitude` is provided")

        if latitude is None and longitude is not None:
            self._raise(self.latitude, "latitude", "`latitude` must be set if `longitude` is provided")

        return self


class AddressResponse(serialization.HttpBodyModel):
    id: int
    latitude: float = fields_v2.LATITUDE
    longitude: float = fields_v2.LONGITUDE
    banId: str | None = fields_v2.BAN_ID_NOT_REQUIRED
    city: str = fields_v2.CITY
    postalCode: str = fields_v2.POSTAL_CODE
    street: str = fields_v2.STREET

    model_config = pydantic_v2.ConfigDict(from_attributes=True)


class SearchAddressResponse(serialization.HttpBodyModel):
    addresses: list[AddressResponse]
