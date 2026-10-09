import logging
import typing

import pydantic

from pcapi.core.educational import schemas
from pcapi.routes.serialization import HttpBodyModel
from pcapi.routes.serialization import HttpQueryParamsModel


if typing.TYPE_CHECKING:
    from pcapi.core.offerers.models import Venue


logger = logging.getLogger(__name__)


class GetRelativeVenuesQueryModel(HttpQueryParamsModel):
    getRelative: bool = False


class VenueDomain(HttpBodyModel):
    id: int
    name: str


class VenueLabelModel(HttpBodyModel):
    id: int
    label: str = pydantic.Field(alias="name")


class OffererModel(HttpBodyModel):
    id: int
    name: str


class VenueModel(HttpBodyModel):
    name: str
    siret: str | None
    address: str | None
    latitude: float | None
    longitude: float | None
    city: str | None
    publicName: str
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
    siren: str
    isPermanent: bool
    offerer: OffererModel
    bannerUrl: str | None
    bannerMeta: dict | None

    @classmethod
    def build(cls, venue: "Venue") -> typing.Self:
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
            address=venue.offererAddress.address.street,
            latitude=float(venue.offererAddress.address.latitude),
            longitude=float(venue.offererAddress.address.longitude),
            city=venue.offererAddress.address.city,
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
            domains=[VenueDomain.model_validate(d) for d in venue.collectiveDomains],
            interventionArea=intervention_area,
            network=venue.collectiveNetwork,
            statusId=venue.venueEducationalStatusId,
            label=VenueLabelModel.model_validate(venue.venueLabel) if venue.venueLabel else None,
            siren=venue.managingOfferer.siren,
            isPermanent=venue.isPermanent,
            offerer=OffererModel.model_validate(venue.managingOfferer),
            bannerUrl=venue.bannerUrl,
            bannerMeta=venue.bannerMeta,
        )


class GetVenuesResponseModel(HttpBodyModel):
    venues: list[VenueModel]


class GetAllVenuesQueryModel(HttpQueryParamsModel):
    page: int | None = pydantic.Field(default=None, gt=0)
    per_page: int | None = pydantic.Field(default=None, gt=0)

    model_config = pydantic.ConfigDict(alias_generator=None)


class PostAdageCulturalPartnerModel(schemas.AdageCulturalPartner, HttpBodyModel):
    pass
