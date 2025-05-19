import enum
from datetime import datetime
from typing import Any
from typing import Iterable

import pydantic.v1 as pydantic_v1
import sqlalchemy.orm as sa_orm
from pydantic.v1.utils import GetterDict
from sqlalchemy.engine import Row

import pcapi.core.offerers.models as offerers_models
import pcapi.core.offerers.repository as offerers_repository
import pcapi.core.offers.models as offers_models
import pcapi.utils.date as date_utils
from pcapi import settings
from pcapi.core.offerers import schemas as offerers_schemas
from pcapi.core.offerers.models import Target
from pcapi.models import db
from pcapi.routes.native.v1.serialization.common_models import AccessibilityComplianceMixin
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import finance_serialize
from pcapi.routes.serialization.address_serialize import AddressResponseModel
from pcapi.routes.serialization.venues_serialize import BannerMetaModel
from pcapi.routes.serialization.venues_serialize import DMSApplicationForEAC
from pcapi.routes.shared import validation
from pcapi.serialization.utils import to_camel
from pcapi.utils.email import sanitize_email


class GetOffererVenueResponseModelGetterDict(GetterDict):
    def get(self, key: str, default: Any = None) -> Any:
        if key == "collectiveDmsApplications":
            return [
                DMSApplicationForEAC.from_orm(collective_ds_application, self._obj.id)
                for collective_ds_application in self._obj.collectiveDmsApplications
            ]
        if key == "hasPartnerPage":
            return self._obj._has_partner_page
        return super().get(key, default)


class GetOffererVenueResponseModel(BaseModel, AccessibilityComplianceMixin):
    adageInscriptionDate: datetime | None
    street: str | None
    bookingEmail: str | None
    city: str | None
    comment: str | None
    departementCode: str | None
    hasCreatedOffer: bool
    hasAdageId: bool
    isVirtual: bool
    isVisibleInApp: bool = True
    name: str
    id: int
    postalCode: str | None
    publicName: str | None
    siret: str | None
    venueTypeCode: offerers_models.VenueTypeCode
    withdrawalDetails: str | None
    collectiveDmsApplications: list[DMSApplicationForEAC]
    hasPartnerPage: bool
    hasVenueProviders: bool
    isPermanent: bool
    bannerUrl: str | None
    bannerMeta: BannerMetaModel | None

    @classmethod
    def from_orm(
        cls,
        venue: offerers_models.Venue,
        ids_of_venues_with_offers: Iterable[int] = (),
    ) -> "GetOffererVenueResponseModel":
        venue.hasCreatedOffer = venue.id in ids_of_venues_with_offers
        venue.hasAdageId = bool(venue.adageId)
        venue.hasVenueProviders = bool(venue.venueProviders)
        return super().from_orm(venue)

    class Config:
        orm_mode = True
        json_encoders = {datetime: date_utils.format_into_utc_date}
        getter_dict = GetOffererVenueResponseModelGetterDict


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
    apiKey: OffererApiKey
    city: str
    dateCreated: datetime
    hasAvailablePricingPoints: bool
    hasDigitalVenueAtLeastOneOffer: bool
    isValidated: bool
    isActive: bool
    # see end of `from_orm()`
    managedVenues: list[GetOffererVenueResponseModel] = []
    name: str
    id: int
    postalCode: str
    siren: str
    street: str | None
    # FIXME (mageoffray, 2023-09-14): optional until we populate the database
    hasValidBankAccount: bool
    hasPendingBankAccount: bool
    hasNonFreeOffer: bool
    venuesWithNonFreeOffersWithoutBankAccounts: list[int]
    hasActiveOffer: bool
    allowedOnAdage: bool
    hasBankAccountWithPendingCorrections: bool
    isOnboarded: bool
    hasHeadlineOffer: bool
    hasPartnerPage: bool

    @classmethod
    def from_orm(cls, row: Row) -> "GetOffererResponseModel":
        offerer: offerers_models.Offerer = row.Offerer

        offerer.apiKey = {
            "maxAllowed": settings.MAX_API_KEY_PER_OFFERER,
            "prefixes": offerers_repository.get_api_key_prefixes(offerer.id),
        }
        venues = (
            db.session.query(offerers_models.Venue)
            .filter_by(managingOffererId=offerer.id)
            .options(sa_orm.joinedload(offerers_models.Venue.collectiveDmsApplications))
            .options(sa_orm.joinedload(offerers_models.Venue.venueProviders))
            .options(sa_orm.joinedload(offerers_models.Venue.googlePlacesInfo))
            .order_by(offerers_models.Venue.common_name)
            .all()
        )

        offerer.hasDigitalVenueAtLeastOneOffer = offerers_repository.has_digital_venue_with_at_least_one_offer(
            offerer.id
        )
        offerer.hasAvailablePricingPoints = any(venue.siret for venue in venues)
        offerer.venuesWithNonFreeOffersWithoutBankAccounts = (
            offerers_repository.get_venues_with_non_free_offers_without_bank_accounts(offerer.id)
        )
        offerer.hasValidBankAccount = row.hasValidBankAccount
        offerer.hasPendingBankAccount = row.hasPendingBankAccount
        offerer.hasNonFreeOffer = row.hasNonFreeOffer
        offerer.hasActiveOffer = row.hasActiveOffer
        offerer.hasBankAccountWithPendingCorrections = row.hasBankAccountWithPendingCorrections
        offerer.isOnboarded = row.isOnboarded
        offerer.hasHeadlineOffer = row.hasHeadlineOffer
        offerer.hasPartnerPage = row.hasPartnerPage
        # We would like the response attribute to be called
        # `managedVenues` but we don't want to use the
        # `Offerer.managedVenues` relationship which does not
        # join-load what we want.
        res = super().from_orm(offerer)
        ids_of_venues_with_offers = offerers_repository.get_ids_of_venues_with_offers([offerer.id])

        res.managedVenues = [
            GetOffererVenueResponseModel.from_orm(venue, ids_of_venues_with_offers) for venue in venues
        ]
        # Behavior in PC Pro for a closed offerer should be the same as for a suspended validated offerer
        res.isValidated = offerer.isValidated or offerer.isClosed  # do now show "en attente de traitement"
        res.isActive = offerer.isActive and not offerer.isClosed
        return res

    class Config:
        orm_mode = True
        json_encoders = {datetime: date_utils.format_into_utc_date}


class GetOffererNameResponseModel(BaseModel):
    id: int
    name: str
    allowedOnAdage: bool

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
    # If `validated_for_user` is true, we only return offerers with
    # which the user has a _validated_ `UserOfferer`. Otherwise, we
    # return all offerers with which the user has a `UserOfferer`, be
    # it validated or not.
    validated_for_user: bool | None
    offerer_id: int | None

    class Config:
        extra = "forbid"


class GetEducationalOffererVenueResponseModel(BaseModel, AccessibilityComplianceMixin):
    city: str | None
    id: int
    isVirtual: bool
    publicName: str | None
    name: str
    postalCode: str | None
    street: str | None
    collectiveInterventionArea: list[str] | None
    collectivePhone: str | None
    collectiveEmail: str | None

    class Config:
        orm_mode = True


class GetEducationalOffererResponseModel(BaseModel):
    id: int
    name: str
    managedVenues: list[GetEducationalOffererVenueResponseModel]
    allowedOnAdage: bool

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
    city: str
    latitude: float | None
    longitude: float | None
    name: str
    postalCode: str
    inseeCode: str | None
    siren: str
    street: str | None
    phoneNumber: str | None

    _validate_phone_number = validation.phone_number_validator("phoneNumber", nullable=True)


class SaveNewOnboardingDataQueryModel(BaseModel):
    address: offerers_schemas.AddressBodyModel
    createVenueWithoutSiret: bool = False
    isOpenToPublic: bool
    publicName: str | None
    siret: str
    target: Target
    token: str
    venueTypeCode: str
    webPresence: str
    phoneNumber: str | None

    _validate_phone_number = validation.phone_number_validator("phoneNumber", nullable=True)

    class Config:
        extra = "forbid"
        anystr_strip_whitespace = True


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


class TopOffersResponseData(offerers_models.TopOffersData):
    offerName: str
    image: offers_models.OfferImage | None
    isHeadlineOffer: bool


class OffererStatsDataModel(BaseModel):
    totalViewsLast30Days: int
    topOffers: list[TopOffersResponseData]
    dailyViews: list[offerers_models.OffererViewsModel]


class GetOffererStatsResponseModel(BaseModel):
    offererId: int
    syncDate: datetime | None
    jsonData: OffererStatsDataModel

    @classmethod
    def build(
        cls,
        *,
        offerer_id: int,
        syncDate: datetime,
        dailyViews: list[dict],  # dicts are serialized from offerers_models.OffererViewsModel
        topOffers: list[dict],  # dicts are serialized from offerers_models.TopOffersData
        total_views_last_30_days: int,
    ) -> "GetOffererStatsResponseModel":
        top_offers_response = []
        if topOffers:
            top_offers_response = [
                TopOffersResponseData(
                    offerName=topOffer["offerName"],
                    offerId=topOffer["offerId"],
                    image=topOffer["image"],
                    numberOfViews=topOffer["numberOfViews"],
                    isHeadlineOffer=topOffer["isHeadlineOffer"],
                )
                for topOffer in topOffers
            ]

        return cls(
            offererId=offerer_id,
            syncDate=syncDate,
            jsonData=OffererStatsDataModel(
                topOffers=top_offers_response,
                totalViewsLast30Days=total_views_last_30_days,
                dailyViews=[offerers_models.OffererViewsModel(**_v) for _v in dailyViews],
            ),
        )


class LinkVenueToBankAccountBodyModel(BaseModel):
    venues_ids: set[int]


class GetOffererV2StatsResponseModel(BaseModel):
    publishedPublicOffers: int
    publishedEducationalOffers: int
    pendingPublicOffers: int
    pendingEducationalOffers: int

    class Config:
        orm_mode = True


class OffererAddressGetterDict(GetterDict):
    def get(self, key: str, default: Any | None = None) -> Any:
        if key == "isLinkedToVenue":
            if self.get("venueId", default) is None:
                return False
            return True
        if key == "label":
            if self.get("common_name", default) is not None:
                return self.get("common_name", default)
        return super().get(key, default)


class GetOffererAddressResponseModel(BaseModel):
    id: int
    label: str | None
    street: str | None
    postalCode: str
    city: str
    isLinkedToVenue: bool
    departmentCode: str | None

    class Config:
        getter_dict = OffererAddressGetterDict
        orm_mode = True


class OffererAddressRequestModel(BaseModel):
    label: str | None
    inseeCode: str
    street: str


class GetOffererAddressesResponseModel(BaseModel):
    __root__: list[GetOffererAddressResponseModel]


class GetOffererAddressesQueryModel(BaseModel):
    onlyWithOffers: bool = False


class PatchOffererAddressRequest(BaseModel):
    label: str


class OffererAddressResponseModel(BaseModel):
    id: int
    label: str | None
    offererId: int
    address: AddressResponseModel

    class Config:
        orm_mode = True


class OffererEligibilityResponseModel(BaseModel):
    offerer_id: int
    has_adage_id: bool | None
    has_ds_application: bool | None
    is_onboarded: bool | None

    class Config:
        allow_population_by_field_name = True
        alias_generator = to_camel
