import logging
import typing

from pydantic.v1 import PositiveInt

from pcapi.core.offerers.models import Venue
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
    domains: typing.Sequence[VenueDomain]
    interventionArea: list[str]
    network: list[str] | None
    statusId: int | None
    label: VenueLabelModel | None
    siren: str
    isPermanent: bool
    isAdmin: bool
    offerer: OffererModel
    bannerUrl: str | None
    bannerMeta: dict | None

    @classmethod
    def from_orm(cls, venue: Venue) -> "VenueModel":
        if venue.offererAddress is not None:
            venue_address = venue.offererAddress.address
            address = venue_address.street
            latitude = float(venue_address.latitude)
            longitude = float(venue_address.longitude)
            city = venue_address.city
        else:
            # TODO(OA): remove this when the virtual venues are migrated
            address = None
            latitude = None
            longitude = None
            city = None

        contact = venue.contact

        email: str | None = None
        if venue.collectiveEmail:
            email = venue.collectiveEmail
        elif contact is not None:
            email = contact.email

        website: str | None = None
        if venue.collectiveWebsite:
            website = venue.collectiveWebsite
        elif contact is not None:
            website = contact.website

        phone_number: str | None = None
        if venue.collectivePhone:
            phone_number = venue.collectivePhone
        elif contact is not None:
            phone_number = contact.phone_number

        intervention_area = [intervention_area.zfill(3) for intervention_area in venue.collectiveInterventionArea or []]

        return cls(
            name=venue.name,
            siret=venue.siret,
            address=address,
            latitude=latitude,
            longitude=longitude,
            city=city,
            publicName=venue.publicName,
            description=venue.description,
            collectiveDescription=venue.collectiveDescription,
            id=venue.id,
            adageId=venue.adageId,
            email=email,
            website=website,
            phoneNumber=phone_number,
            audioDisabilityCompliant=venue.audioDisabilityCompliant,
            mentalDisabilityCompliant=venue.mentalDisabilityCompliant,
            motorDisabilityCompliant=venue.motorDisabilityCompliant,
            visualDisabilityCompliant=venue.visualDisabilityCompliant,
            domains=venue.collectiveDomains,
            interventionArea=intervention_area,
            network=venue.collectiveNetwork,
            statusId=venue.venueEducationalStatusId,
            label=venue.venueLabel,
            siren=venue.managingOfferer.siren,
            isPermanent=venue.isPermanent,
            isAdmin=venue.venueTypeCode == VenueTypeCode.ADMINISTRATIVE,
            offerer=venue.managingOfferer,
            bannerUrl=venue.bannerUrl,
            bannerMeta=venue.bannerMeta,
        )

    class Config:
        orm_mode = True


class GetVenuesResponseModel(BaseModel):
    venues: list[VenueModel]


class GetAllVenuesQueryModel(BaseModel):
    page: PositiveInt | None
    per_page: PositiveInt | None
