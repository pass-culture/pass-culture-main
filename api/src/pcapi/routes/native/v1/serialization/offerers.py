import typing

from pcapi.core.offerers import models as offerers_models
from pcapi.routes.serialization import venues_serialize

from . import BaseModel


class VenueAccessibilityModel(BaseModel):
    audioDisability: typing.Optional[bool]
    mentalDisability: typing.Optional[bool]
    motorDisability: typing.Optional[bool]
    visualDisability: typing.Optional[bool]


class VenueResponse(BaseModel):
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
    venueTypeCode: typing.Optional[offerers_models.VenueTypeCodeKey]
    description: typing.Optional[venues_serialize.VenueDescription]  # type: ignore
    contact: typing.Optional[venues_serialize.VenueContactModel]
    accessibility: VenueAccessibilityModel
