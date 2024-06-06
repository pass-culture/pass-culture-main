from datetime import datetime
import enum
from typing import Iterable

import pydantic.v1 as pydantic_v1
from sqlalchemy.engine import Row
import sqlalchemy.orm as sqla_orm

from pcapi import settings
import pcapi.core.offerers.models as offerers_models
from pcapi.core.offerers.models import Target
import pcapi.core.offerers.repository as offerers_repository
import pcapi.core.offers.models as offers_models
from pcapi.routes.native.v1.serialization.common_models import AccessibilityComplianceMixin
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import finance_serialize
from pcapi.routes.serialization.venues_serialize import BannerMetaModel
from pcapi.routes.serialization.venues_serialize import DMSApplicationForEAC
import pcapi.utils.date as date_utils
from pcapi.utils.email import sanitize_email


class GetOffererVenueResponseModel(BaseModel, AccessibilityComplianceMixin):
    adageInscriptionDate: datetime | None
    street: str | None
    bookingEmail: str | None
    city: str | None
    comment: str | None
    departementCode: str | None
    demarchesSimplifieesApplicationId: int | None
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
    street: str | None
    # FIXME (mageoffray, 2023-09-14): optional until we populate the database
    hasValidBankAccount: bool
    hasPendingBankAccount: bool
    hasNonFreeOffer: bool
    venuesWithNonFreeOffersWithoutBankAccounts: list[int]
    hasActiveOffer: bool
    allowedOnAdage: bool
    hasBankAccountWithPendingCorrections: bool

    @classmethod
    def from_orm(cls, row: Row) -> "GetOffererResponseModel":
        offerer: offerers_models.Offerer = row.Offerer

        offerer.apiKey = {
            "maxAllowed": settings.MAX_API_KEY_PER_OFFERER,
            "prefixes": offerers_repository.get_api_key_prefixes(offerer.id),
        }
        venues = (
            offerers_models.Venue.query.filter_by(managingOffererId=offerer.id)
            .options(sqla_orm.joinedload(offerers_models.Venue.reimbursement_point_links))
            .options(sqla_orm.joinedload(offerers_models.Venue.bankInformation))
            .options(sqla_orm.joinedload(offerers_models.Venue.collectiveDmsApplications))
            .options(sqla_orm.joinedload(offerers_models.Venue.venueProviders))
            .options(sqla_orm.joinedload(offerers_models.Venue.googlePlacesInfo))
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
        offerer.hasValidBankAccount = row.hasValidBankAccount
        offerer.hasPendingBankAccount = row.hasPendingBankAccount
        offerer.hasNonFreeOffer = row.hasNonFreeOffer
        offerer.hasActiveOffer = row.hasActiveOffer
        offerer.hasBankAccountWithPendingCorrections = row.hasBankAccountWithPendingCorrections

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
    # FIXME (dbaty, 2022-05-04): rename to something clearer, e.g. `include_non_validated_user_offerers`
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
    collectiveSubCategoryId: str | None

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
    siren: str
    street: str | None


class SaveNewOnboardingDataQueryModel(BaseModel):
    banId: str | None
    city: str
    createVenueWithoutSiret: bool = False
    latitude: float
    longitude: float
    postalCode: str
    publicName: str | None
    siret: str
    street: str | None
    target: Target
    venueTypeCode: str
    webPresence: str
    token: str

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

    @classmethod
    def build(cls, offer_id: int, number_of_views: int) -> "TopOffersResponseData":
        # This adds a call to the db for every offer, but it's not a big deal since we only get the top 3 offers
        offer = offers_models.Offer.query.get(offer_id)
        if not offer:
            raise ValueError(f"Offer with id {offer_id} does not exist")
        return cls(offerId=offer_id, offerName=offer.name, image=offer.image, numberOfViews=number_of_views)


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
        offerer_id: int,
        syncDate: datetime,
        dailyViews: list[dict],  # dicts are serialized from offerers_models.OffererViewsModel
        topOffers: list[dict],  # dicts are serialized from offerers_models.TopOffersData
        total_views_last_30_days: int,
    ) -> "GetOffererStatsResponseModel":
        top_offers_response = []
        if topOffers:
            top_offers_response = [
                TopOffersResponseData.build(topOffer["offerId"], topOffer["numberOfViews"]) for topOffer in topOffers
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


class AddressResponseModel(BaseModel):
    id: int
    banId: str | None
    inseeCode: str | None
    postalCode: str
    street: str | None
    city: str
    latitude: float
    longitude: float

    class Config:
        orm_mode = True

    @pydantic_v1.validator("latitude", "longitude")
    def round(cls, value: float) -> float:
        """Rounding to five digits to keep consistency
        with the model definition.
        """
        return round(value, 5)


class GetOffererAddressResponseModel(BaseModel):
    id: int
    label: str | None
    street: str | None
    postalCode: str
    city: str
    isEditable: bool

    @classmethod
    def from_orm(cls, offerer_address: offerers_models.OffererAddress) -> "GetOffererAddressResponseModel":
        offerer_address.street = offerer_address.address.street
        offerer_address.postalCode = offerer_address.address.postalCode
        offerer_address.city = offerer_address.address.city
        return super().from_orm(offerer_address)

    class Config:
        orm_mode = True


class GetOffererAddressesResponseModel(BaseModel):
    __root__: list[GetOffererAddressResponseModel]
