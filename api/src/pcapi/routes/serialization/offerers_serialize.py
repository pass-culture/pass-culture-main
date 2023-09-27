from datetime import datetime
import enum
from typing import Iterable

import pydantic.v1 as pydantic_v1
import sqlalchemy.orm as sqla_orm

from pcapi import settings
import pcapi.core.offerers.models as offerers_models
from pcapi.core.offerers.models import Target
import pcapi.core.offerers.repository as offerers_repository
from pcapi.domain.demarches_simplifiees import DMS_TOKEN_PRO_PREFIX
from pcapi.routes.native.v1.serialization.common_models import AccessibilityComplianceMixin
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import finance_serialize
from pcapi.routes.serialization.venues_serialize import DMSApplicationForEAC
import pcapi.utils.date as date_utils
from pcapi.utils.email import sanitize_email


class GetOffererVenueResponseModel(BaseModel, AccessibilityComplianceMixin):
    adageInscriptionDate: datetime | None
    address: str | None
    bookingEmail: str | None
    city: str | None
    comment: str | None
    departementCode: str | None
    hasMissingReimbursementPoint: bool
    hasPendingBankInformationApplication: bool | None
    demarchesSimplifieesApplicationId: int | None
    hasCreatedOffer: bool
    hasAdageId: bool
    isVirtual: bool
    name: str
    id: int
    postalCode: str | None
    publicName: str | None
    siret: str | None
    venueTypeCode: offerers_models.VenueTypeCode
    withdrawalDetails: str | None
    collectiveDmsApplications: list[DMSApplicationForEAC]

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


class PostOffererResponseModel(BaseModel):
    name: str
    id: int
    siren: str

    class Config:
        orm_mode = True


# GetOffererResponseModel includes sensitive information and can be returned only if authenticated user has a validated
# access to the offerer. During subscription process, use PostOffererResponseModel
class GetOffererResponseModel(BaseModel):
    address: str | None
    apiKey: OffererApiKey
    city: str
    dateCreated: datetime
    demarchesSimplifieesApplicationId: str | None
    hasAvailablePricingPoints: bool
    hasDigitalVenueAtLeastOneOffer: bool
    isValidated: bool
    isActive: bool
    # see end of `from_orm()`
    managedVenues: list[GetOffererVenueResponseModel] = []
    name: str
    id: int
    postalCode: str
    # FIXME (dbaty, 2020-11-09): optional until we populate the database (PC-5693)
    siren: str | None
    # FIXME (mageoffray, 2023-09-14): optional until we populate the database
    dsToken: str | None
    hasValidBankAccount: bool
    hasPendingBankAccount: bool
    venuesWithNonFreeOffersWithoutBankAccounts: list[int]

    @classmethod
    def from_orm(cls, offerer: offerers_models.Offerer) -> "GetOffererResponseModel":
        offerer.dsToken = DMS_TOKEN_PRO_PREFIX + offerer.dsToken
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
        offerer.venuesWithNonFreeOffersWithoutBankAccounts = (
            offerers_repository.get_venues_with_non_free_offers_without_bank_accounts(offerer.id)
        )

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
    id: int
    name: str

    class Config:
        orm_mode = True


class OffererMemberStatus(enum.Enum):
    VALIDATED = "validated"
    PENDING = "pending"


class GetOffererMemberResponseModel(BaseModel):
    email: str
    status: OffererMemberStatus


class GetOffererMembersResponseModel(BaseModel):
    members: list[GetOffererMemberResponseModel]


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
    id: int
    isVirtual: bool
    publicName: str | None
    name: str
    postalCode: str | None
    collectiveInterventionArea: list[str] | None
    collectivePhone: str | None
    collectiveEmail: str | None
    collectiveSubCategoryId: str | None

    class Config:
        orm_mode = True


class GetEducationalOffererResponseModel(BaseModel):
    id: int
    name: str
    managedVenues: list[GetEducationalOffererVenueResponseModel]

    class Config:
        orm_mode = True


class GetEducationalOfferersResponseModel(BaseModel):
    educationalOfferers: list[GetEducationalOffererResponseModel]

    class Config:
        orm_mode = True


class GetEducationalOfferersQueryModel(BaseModel):
    offerer_id: int | None

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
    address: str | None
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
    token: str

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


class InviteMemberQueryModel(BaseModel):
    email: str

    @pydantic_v1.validator("email")
    @classmethod
    def validate_email(cls, email: str) -> str:
        try:
            return sanitize_email(email)
        except Exception as e:
            raise ValueError(email) from e


class GetOffererBankAccountsResponseModel(BaseModel):
    id: int
    bankAccounts: list[finance_serialize.BankAccountResponseModel]
    managedVenues: list[finance_serialize.ManagedVenues]

    class Config:
        orm_mode = True
