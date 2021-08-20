import typing

from pcapi.core.offerers import models as offerers_models
from pcapi.routes.serialization import venues_serialize
from pcapi.serialization.utils import to_camel

from . import BaseModel


class VenueResponse(BaseModel):
    class Config:
        orm_mode = True
        alias_generator = to_camel
        allow_population_by_field_name = True

    id: int
    name: str
    latitude: typing.Optional[float]
    longitude: typing.Optional[float]
    city: typing.Optional[str]
    publicName: typing.Optional[str]
    isVirtual: bool
    isPermanent: typing.Optional[bool]
    withdrawalDetails: typing.Optional[str]
    address: typing.Optional[str]
    postalCode: typing.Optional[str]
    venueTypeCode: typing.Optional[offerers_models.VenueTypeCode]
    description: typing.Optional[venues_serialize.VenueDescription]  # type: ignore
    audioDisabilityCompliant: typing.Optional[bool]
    mentalDisabilityCompliant: typing.Optional[bool]
    motorDisabilityCompliant: typing.Optional[bool]
    visualDisabilityCompliant: typing.Optional[bool]
    contact: typing.Optional[venues_serialize.VenueContactModel]
