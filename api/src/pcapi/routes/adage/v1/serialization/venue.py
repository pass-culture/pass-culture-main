from typing import Any

from pydantic import PositiveInt

from pcapi.core.offerers.models import Venue
from pcapi.core.offerers.models import VenueContact
from pcapi.routes.serialization import BaseModel


class BaseVenueModel(BaseModel):
    name: str
    address: str | None
    latitude: float | None
    longitude: float | None
    city: str | None
    publicName: str | None
    description: str | None
    id: int
    adageId: str | None
    email: str | None
    website: str | None
    phoneNumber: str | None
    audioDisabilityCompliant: bool | None
    mentalDisabilityCompliant: bool | None
    motorDisabilityCompliant: bool | None
    visualDisabilityCompliant: bool | None

    @classmethod
    def from_orm(cls: Any, venue: Venue):  # type: ignore
        contact: VenueContact | None = venue.contact
        if contact is not None:
            venue.email = contact.email
            venue.website = contact.website
            venue.phoneNumber = contact.phone_number

        return super().from_orm(venue)

    class Config:
        orm_mode = True


class VenueModelWithOptionalSiret(BaseVenueModel):
    siret: str | None


class VenueModelWithRequiredSiret(BaseVenueModel):
    siret: str


class GetVenuesBySiretResponseModel(BaseModel):
    venues: list[VenueModelWithRequiredSiret]


class GetVenuesWithOptionalSiretResponseModel(BaseModel):
    venues: list[VenueModelWithOptionalSiret]


class GetAllVenuesQueryModel(BaseModel):
    page: PositiveInt | None
    per_page: PositiveInt | None
