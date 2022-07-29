from typing import TYPE_CHECKING

from pydantic import PositiveInt

from pcapi.core.offerers.models import Venue
from pcapi.core.offerers.models import VenueContact
from pcapi.routes.serialization import BaseModel


if TYPE_CHECKING:
    from typing import Type
    from typing import TypeVar

    # Create a generic variable that can be 'BaseVenueModel', or any subclass.
    VenueModel = TypeVar("VenueModel", bound="BaseVenueModel")


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
