import typing

from pcapi.core.offerers import models as offerers_models
from pcapi.routes.serialization import venues_serialize
from pcapi.serialization.utils import to_camel

from . import BaseModel


class VenueAccessibilityModel(BaseModel):
    audioDisability: typing.Optional[bool]
    mentalDisability: typing.Optional[bool]
    motorDisability: typing.Optional[bool]
    visualDisability: typing.Optional[bool]


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
    contact: typing.Optional[venues_serialize.VenueContactModel]
    accessibility: VenueAccessibilityModel

    @classmethod
    def from_orm(cls, venue: offerers_models.Venue) -> "VenueResponse":
        venue.accessibility = {
            "audioDisability": venue.audioDisabilityCompliant,
            "mentalDisability": venue.mentalDisabilityCompliant,
            "motorDisability": venue.motorDisabilityCompliant,
            "visualDisability": venue.visualDisabilityCompliant,
        }

        return super().from_orm(venue)
