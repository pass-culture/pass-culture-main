import logging

from pydantic.v1 import PositiveInt

from pcapi.core.offerers.models import Venue
from pcapi.core.offerers.models import VenueContact
from pcapi.core.offerers.models import VenueLabel
from pcapi.core.offerers.models import VenueTypeCode
from pcapi.routes.serialization import BaseModel


logger = logging.getLogger(__name__)


class GetRelativeVenuesQueryModel(BaseModel):
    getRelative: bool = False


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


class OffererModel(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class VenueModel(BaseModel):
    name: str
    siret: str | None
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
    domains: list[VenueDomain] | None
    interventionArea: list[str] | None
    network: list[str] | None
    statusId: int | None
    label: VenueLabelModel | None
    siren: str | None  # TODO (jcicurel) : remove | None
    isPermanent: bool | None
    isAdmin: bool | None
    offerer: OffererModel | None
    bannerUrl: str | None
    bannerMeta: dict | None

    @classmethod
    def from_orm(cls, venue: Venue) -> "VenueModel":
        result: "VenueModel" = super().from_orm(venue)

        contact: VenueContact | None = venue.contact

        if venue.collectiveEmail:
            result.email = venue.collectiveEmail
        elif contact is not None:
            result.email = contact.email

        if venue.collectiveWebsite:
            result.website = venue.collectiveWebsite
        elif contact is not None:
            result.website = contact.website

        if venue.collectivePhone:
            result.phoneNumber = venue.collectivePhone
        elif contact is not None:
            result.phoneNumber = contact.phone_number

        result.domains = [VenueDomain.from_orm(domain) for domain in venue.collectiveDomains]
        result.interventionArea = [
            intervention_area.zfill(3) for intervention_area in venue.collectiveInterventionArea or []
        ]
        result.network = venue.collectiveNetwork
        result.statusId = venue.venueEducationalStatusId
        result.label = VenueLabelModel.from_orm(venue.venueLabel) if venue.venueLabel is not None else None
        result.siren = venue.managingOfferer.siren
        result.isAdmin = venue.venueTypeCode == VenueTypeCode.ADMINISTRATIVE
        result.offerer = OffererModel.from_orm(venue.managingOfferer)

        if venue.offererAddress is None:
            # we only use this model on venues with (isVirtual=False) that should have an offererAddress
            logger.error("Found venue with id %s without offererAddress", venue.id)

            result.address = None
            result.latitude = None
            result.longitude = None
            result.city = None
        else:
            address = venue.offererAddress.address
            result.address = address.street
            result.latitude = float(address.latitude)
            result.longitude = float(address.longitude)
            result.city = address.city

        return result

    class Config:
        orm_mode = True


class GetVenuesResponseModel(BaseModel):
    venues: list[VenueModel]


class GetAllVenuesQueryModel(BaseModel):
    page: PositiveInt | None
    per_page: PositiveInt | None
