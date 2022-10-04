from typing import TYPE_CHECKING

from pydantic import PositiveInt

from pcapi.core.offerers.models import Venue
from pcapi.core.offerers.models import VenueContact
from pcapi.core.offerers.models import VenueLabel
from pcapi.routes.serialization import BaseModel


if TYPE_CHECKING:
    from typing import Type
    from typing import TypeVar

    # Create a generic variable that can be 'BaseVenueModel', or any subclass.
    VenueModel = TypeVar("VenueModel", bound="BaseVenueModel")


class VenueDomain(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class VenueLabelModel(BaseModel):
    id: int
    name: str

    @classmethod
    def from_orm(cls, venue_label: VenueLabel) -> "VenueLabelModel":
        venue_label.name = venue_label.label
        return super().from_orm(venue_label)

    class Config:
        orm_mode = True


class BaseVenueModel(BaseModel):
    name: str
    address: str | None
    latitude: float | None
    longitude: float | None
    city: str | None
    publicName: str | None
    description: str | None
    collectiveDescription: str | None
    id: int
    adageId: str | None
    email: str | None
    website: str | None
    phoneNumber: str | None
    audioDisabilityCompliant: bool | None
    mentalDisabilityCompliant: bool | None
    motorDisabilityCompliant: bool | None
    visualDisabilityCompliant: bool | None
    domains: list[VenueDomain]
    interventionArea: list[str]
    network: list[str] | None
    statusId: int | None
    label: VenueLabelModel | None

    @classmethod
    def from_orm(cls: "Type[VenueModel]", venue: Venue) -> "VenueModel":
        contact: VenueContact | None = venue.contact

        if venue.collectiveEmail:
            venue.email = venue.collectiveEmail
        elif contact is not None:
            venue.email = contact.email

        if venue.collectiveWebsite:
            venue.website = venue.collectiveWebsite
        elif contact is not None:
            venue.website = contact.website

        if venue.collectivePhone:
            venue.phoneNumber = venue.collectivePhone
        elif contact is not None:
            venue.phoneNumber = contact.phone_number

        venue.domains = venue.collectiveDomains
        venue.interventionArea = [
            intervention_area.zfill(3) for intervention_area in venue.collectiveInterventionArea or []
        ]
        venue.network = venue.collectiveNetwork
        venue.statusId = venue.venueEducationalStatusId

        venue.label = venue.venueLabel

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
