from datetime import datetime
from typing import Iterable

import sqlalchemy.orm as sqla_orm

from pcapi import settings
import pcapi.core.offerers.models as offerers_models
from pcapi.core.offerers.models import Target
import pcapi.core.offerers.repository as offerers_repository
from pcapi.routes.native.v1.serialization.common_models import AccessibilityComplianceMixin
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization.venues_serialize import DMSApplicationForEAC
from pcapi.serialization.utils import humanize_field
import pcapi.utils.date as date_utils


class GetOffererVenueResponseModel(BaseModel, AccessibilityComplianceMixin):
    adageInscriptionDate: datetime | None
    address: str | None
    bookingEmail: str | None
    city: str | None
    comment: str | None
    departementCode: str | None
    hasMissingReimbursementPoint: bool
    hasCreatedOffer: bool
    hasAdageId: bool
    id: str
    isVirtual: bool
    managingOffererId: str
    name: str
    nonHumanizedId: int
    postalCode: str | None
    publicName: str | None
    siret: str | None
    venueLabelId: str | None
    venueTypeCode: offerers_models.VenueTypeCode
    withdrawalDetails: str | None
    collectiveDmsApplications: list[DMSApplicationForEAC]
    _humanize_id = humanize_field("id")
    _humanize_managing_offerer_id = humanize_field("managingOffererId")
    _humanize_venue_label_id = humanize_field("venueLabelId")

    @classmethod
    def from_orm(
        cls,
        venue: offerers_models.Venue,
        ids_of_venues_with_offers: Iterable[int] = (),
    ) -> "GetOffererVenueResponseModel":
        now = datetime.utcnow()
        venue.hasMissingReimbursementPoint = not (
            any(
                (
                    now > link.timespan.lower and (link.timespan.upper is None or now < link.timespan.upper)
                    for link in venue.reimbursement_point_links
                )
            )
            or venue.hasPendingBankInformationApplication
        )
        venue.hasCreatedOffer = venue.id in ids_of_venues_with_offers
        venue.hasAdageId = bool(venue.adageId)
        return super().from_orm(venue)

    class Config:
        orm_mode = True
        json_encoders = {datetime: date_utils.format_into_utc_date}


class OffererApiKey(BaseModel):
    maxAllowed: int
    prefixes: list[str]


class GetOffererResponseModel(BaseModel):
    address: str | None
    apiKey: OffererApiKey
    city: str
    dateCreated: datetime
    dateModifiedAtLastProvider: datetime | None
    demarchesSimplifieesApplicationId: str | None
    fieldsUpdated: list[str]
    hasAvailablePricingPoints: bool
    hasDigitalVenueAtLeastOneOffer: bool
    id: str
    idAtProviders: str | None
    isValidated: bool
    isActive: bool
    lastProviderId: str | None
    # see end of `from_orm()`
    managedVenues: list[GetOffererVenueResponseModel] = []
    name: str
    nonHumanizedId: int
    postalCode: str
    # FIXME (dbaty, 2020-11-09): optional until we populate the database (PC-5693)
    siren: str | None

    _humanize_id = humanize_field("id")

    @classmethod
    def from_orm(cls, offerer: offerers_models.Offerer) -> "GetOffererResponseModel":
        offerer.apiKey = {
            "maxAllowed": settings.MAX_API_KEY_PER_OFFERER,
            "prefixes": offerers_repository.get_api_key_prefixes(offerer.id),
        }
        venues = (
            offerers_models.Venue.query.filter_by(managingOffererId=offerer.id)
            .options(sqla_orm.joinedload(offerers_models.Venue.reimbursement_point_links))
            .options(sqla_orm.joinedload(offerers_models.Venue.bankInformation))
            .options(sqla_orm.joinedload(offerers_models.Venue.collectiveDmsApplications))
            .order_by(offerers_models.Venue.common_name)
            .all()
        )

        offerer.hasDigitalVenueAtLeastOneOffer = offerers_repository.has_digital_venue_with_at_least_one_offer(
            offerer.id
        )
        offerer.hasAvailablePricingPoints = any(venue.siret for venue in offerer.managedVenues)

        # We would like the response attribute to be called
        # `managedVenues` but we don't want to use the
        # `Offerer.managedVenues` relationship which does not
        # join-load what we want.
        res = super().from_orm(offerer)
        ids_of_venues_with_offers = offerers_repository.get_ids_of_venues_with_offers([offerer.id])

        res.managedVenues = [
            GetOffererVenueResponseModel.from_orm(venue, ids_of_venues_with_offers) for venue in venues
        ]
        return res

    class Config:
        orm_mode = True
        json_encoders = {datetime: date_utils.format_into_utc_date}


class GetOffererNameResponseModel(BaseModel):
    nonHumanizedId: int
    name: str

    class Config:
        orm_mode = True


class GetOfferersNamesResponseModel(BaseModel):
    offerersNames: list[GetOffererNameResponseModel]

    class Config:
        orm_mode = True


class GetOfferersNamesQueryModel(BaseModel):
    validated: bool | None
    # FIXME (dbaty, 2022-05-04): rename to something clearer, e.g. `include_non_validated_user_offerers`
    validated_for_user: bool | None
    offerer_id: int | None

    class Config:
        extra = "forbid"


class GetEducationalOffererVenueResponseModel(BaseModel, AccessibilityComplianceMixin):
    address: str | None
    city: str | None
    id: str
    nonHumanizedId: int
    isVirtual: bool
    publicName: str | None
    name: str
    postalCode: str | None
    collectiveInterventionArea: list[str] | None
    collectivePhone: str | None
    collectiveEmail: str | None
    collectiveSubCategoryId: str | None
    _humanize_id = humanize_field("id")

    class Config:
        orm_mode = True


class GetEducationalOffererResponseModel(BaseModel):
    nonHumanizedId: int
    name: str
    managedVenues: list[GetEducationalOffererVenueResponseModel]

    class Config:
        orm_mode = True


class GetEducationalOfferersResponseModel(BaseModel):
    educationalOfferers: list[GetEducationalOffererResponseModel]

    class Config:
        orm_mode = True


class GetEducationalOfferersQueryModel(BaseModel):
    offerer_id: str | None

    class Config:
        extra = "forbid"


class GenerateOffererApiKeyResponse(BaseModel):
    apiKey: str


class CreateOffererQueryModel(BaseModel):
    address: str | None
    city: str
    latitude: float | None
    longitude: float | None
    name: str
    postalCode: str
    siren: str


class SaveNewOnboardingDataQueryModel(BaseModel):
    address: str
    city: str
    createVenueWithoutSiret: bool = False
    latitude: float
    longitude: float
    postalCode: str
    publicName: str | None
    siret: str
    target: Target
    venueTypeCode: str
    webPresence: str

    class Config:
        extra = "forbid"
        anystr_strip_whitespace = True


class OffererReimbursementPointResponseModel(BaseModel):
    venueId: int
    venueName: str
    iban: str


class OffererReimbursementPointListResponseModel(BaseModel):
    __root__: list[OffererReimbursementPointResponseModel]


class OffererStatsResponseModel(BaseModel):
    dashboardUrl: str
