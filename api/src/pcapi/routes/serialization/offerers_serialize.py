import enum
from datetime import datetime
from typing import Any
from typing import Iterable

import pydantic as pydantic_v2
import pydantic.v1 as pydantic_v1
import sqlalchemy.orm as sa_orm
from pydantic.v1.utils import GetterDict
from sqlalchemy.engine import Row

import pcapi.core.offerers.models as offerers_models
import pcapi.core.offerers.repository as offerers_repository
import pcapi.core.offers.models as offers_models
import pcapi.utils.date as date_utils
from pcapi.core.offerers import schemas as offerers_schemas
from pcapi.core.offerers.models import Target
from pcapi.core.subscription.phone_validation.exceptions import InvalidPhoneNumber
from pcapi.models import db
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import HttpBodyModel
from pcapi.routes.serialization import HttpQueryParamsModel
from pcapi.routes.serialization import address_serialize
from pcapi.routes.serialization import finance_serialize
from pcapi.routes.serialization.venues_serialize import BannerMetaModel
from pcapi.routes.serialization.venues_serialize import DMSApplicationForEAC
from pcapi.routes.shared import validation
from pcapi.serialization.exceptions import PydanticError
from pcapi.serialization.utils import to_camel
from pcapi.utils import phone_number
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
        if key == "activity":
            if not self._obj.activity or self._obj.activity == offerers_models.Activity.NOT_ASSIGNED:
                return None
            return offerers_models.DisplayableActivity[self._obj.activity.name]
        return super().get(key, default)


class GetOffererVenueResponseModel(BaseModel):
    bookingEmail: str | None
    hasCreatedOffer: bool
    hasAdageId: bool
    isVirtual: bool
    name: str
    id: int
    publicName: str
    siret: str | None
    venueTypeCode: offerers_models.VenueTypeCode | None
    activity: offerers_models.DisplayableActivity | None
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


# GetOffererResponseModel includes sensitive information and can be returned only if authenticated user has a validated
# access to the offerer. During subscription process, use PostOffererResponseModel
class GetOffererResponseModel(BaseModel):
    hasAvailablePricingPoints: bool
    hasDigitalVenueAtLeastOneOffer: bool
    isValidated: bool
    isActive: bool
    # see end of `from_orm()`
    managedVenues: list[GetOffererVenueResponseModel] = []
    name: str
    id: int
    siren: str
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
    isCaledonian: bool
    canDisplayHighlights: bool

    @classmethod
    def from_orm(cls, row: Row) -> "GetOffererResponseModel":
        offerer: offerers_models.Offerer = row.Offerer
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
        offerer.isCaledonian = offerer.is_caledonian
        offerer.canDisplayHighlights = row.canDisplayHighlights
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


class OffererMemberStatus(enum.Enum):
    VALIDATED = "validated"
    PENDING = "pending"


class GetOffererMemberResponseModel(HttpBodyModel):
    email: str
    status: OffererMemberStatus


class GetOffererMembersResponseModel(HttpBodyModel):
    members: list[GetOffererMemberResponseModel]


class GetOfferersNamesQueryModel(HttpQueryParamsModel):
    validated: bool | None = None
    # If `validated_for_user` is true, we only return offerers with
    # which the user has a _validated_ `UserOfferer`. Otherwise, we
    # return all offerers with which the user has a `UserOfferer`, be
    # it validated or not.
    validated_for_user: bool | None = None
    offerer_id: int | None = None


class GetEducationalOffererVenueResponseModel(HttpBodyModel):
    id: int
    isVirtual: bool
    publicName: str
    name: str
    collectiveInterventionArea: list[str] | None = None
    collectivePhone: str | None = None
    collectiveEmail: str | None = None
    # address data
    city: str | None = None
    postalCode: str | None = None
    street: str | None = None
    # accessibility
    audioDisabilityCompliant: bool | None = None
    mentalDisabilityCompliant: bool | None = None
    motorDisabilityCompliant: bool | None = None
    visualDisabilityCompliant: bool | None = None

    @classmethod
    def build(cls, venue: offerers_models.Venue) -> "GetEducationalOffererVenueResponseModel":
        return cls(
            id=venue.id,
            isVirtual=venue.isVirtual,
            publicName=venue.publicName,
            name=venue.name,
            collectiveInterventionArea=venue.collectiveInterventionArea,
            collectivePhone=venue.collectivePhone,
            collectiveEmail=venue.collectiveEmail,
            # accessibility
            audioDisabilityCompliant=venue.audioDisabilityCompliant,
            mentalDisabilityCompliant=venue.mentalDisabilityCompliant,
            motorDisabilityCompliant=venue.motorDisabilityCompliant,
            visualDisabilityCompliant=venue.visualDisabilityCompliant,
            # data coming from `offererAddress.address`
            city=venue.offererAddress.address.city,
            postalCode=venue.offererAddress.address.postalCode,
            street=venue.offererAddress.address.street,
        )


class GetEducationalOffererResponseModel(HttpBodyModel):
    id: int
    name: str
    managedVenues: list[GetEducationalOffererVenueResponseModel]
    allowedOnAdage: bool

    # TODO(xordoquy): remove build once the soft delete lib is fixed
    @classmethod
    def build(cls, offerer: offerers_models.Offerer) -> "GetEducationalOffererResponseModel":
        return cls(
            id=offerer.id,
            name=offerer.name,
            managedVenues=[
                GetEducationalOffererVenueResponseModel.build(venue)
                for venue in offerer.managedVenues
                if not venue.isSoftDeleted
            ],
            allowedOnAdage=offerer.allowedOnAdage,
        )


class GetEducationalOfferersResponseModel(HttpBodyModel):
    educational_offerers: list[GetEducationalOffererResponseModel]


class GetEducationalOfferersQueryModel(HttpQueryParamsModel):
    offerer_id: int | None = None


class CreateOffererBodyModel(HttpBodyModel):
    name: str
    siren: str
    phone_number: str | None = None
    # address data
    city: str
    postal_code: str
    street: str | None = None
    insee_code: str | None = None
    longitude: float | None = None
    latitude: float | None = None

    @pydantic_v2.field_validator("phone_number", mode="before")
    @classmethod
    def validate_field(cls, value: str | None) -> str | None:
        if value is None:
            return None

        try:
            parsed = phone_number.parse_phone_number(value)
        except InvalidPhoneNumber:
            raise PydanticError("Ce numéro de telephone ne semble pas valide")

        return phone_number.get_formatted_phone_number(parsed)


class SaveNewOnboardingDataQueryModel(BaseModel):
    activity: offerers_models.ActivityOpenToPublic | offerers_models.ActivityNotOpenToPublic
    address: address_serialize.LocationBodyModel
    culturalDomains: list[str] | None = pydantic_v1.Field(min_items=1)
    createVenueWithoutSiret: bool = False
    isOpenToPublic: bool
    publicName: str | None
    siret: str
    target: Target
    token: str
    webPresence: str
    phoneNumber: str | None

    _validate_phone_number = validation.phone_number_validator("phoneNumber", nullable=True)

    class Config:
        extra = "forbid"
        anystr_strip_whitespace = True


class InviteMemberQueryModel(BaseModel):
    email: str

    @pydantic_v1.validator("email")
    @classmethod
    def validate_email(cls, email: str) -> str:
        try:
            return sanitize_email(email)
        except Exception as e:
            raise ValueError(email) from e


class GetOffererBankAccountsResponseModel(HttpBodyModel):
    id: int
    bank_accounts: list[finance_serialize.BankAccountResponseModel]
    managed_venues: list[finance_serialize.ManagedVenue]


class TopOffersResponseData(offerers_models.TopOffersData):
    offerName: str
    image: offers_models.OfferImage | None
    isHeadlineOffer: bool

    class Config:
        alias_generator = to_camel


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


class VenueMonthlyViewModel(BaseModel):
    month: int
    views: int


class VenueStatsDataModel(BaseModel):
    total_views_last_30_days: int
    top_offers: list[TopOffersResponseData]
    monthly_views: list[VenueMonthlyViewModel]

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True


class GetVenueStatsResponseModel(BaseModel):
    venue_id: int
    json_data: VenueStatsDataModel

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True


class LinkVenueToBankAccountBodyModel(HttpBodyModel):
    venues_ids: set[int]


class GetOffererV2StatsResponseModel(HttpBodyModel):
    published_public_offers: int
    published_educational_offers: int
    pending_public_offers: int
    pending_educational_offers: int


class GetOffererAddressResponseModel(HttpBodyModel):
    id: int
    label: str | None = None
    street: str | None = None
    postal_code: str
    city: str
    department_code: str | None = None
    # this field won't be returned, it is here only to serve as a fallback
    # value if label=None
    common_name: str | None = pydantic_v2.Field(exclude=True, default=None)

    @pydantic_v2.field_serializer("label", mode="plain")
    def label_or_common_name(self, value: str | None) -> str | None:
        return value or self.common_name

    model_config = pydantic_v2.ConfigDict(extra="ignore")


class GetOffererAddressesResponseModel(pydantic_v2.RootModel):
    root: list[GetOffererAddressResponseModel]


class GetOffererAddressesQueryModel(HttpQueryParamsModel):
    with_offers_option: offerers_schemas.GetOffererAddressesWithOffersOption | None = None


class OffererEligibilityResponseModel(HttpBodyModel):
    offerer_id: int
    has_adage_id: bool | None = None
    has_ds_application: bool | None = None
    is_onboarded: bool | None = None


class TopOffersByConsultationModel(HttpBodyModel):
    offerId: str
    totalViewsLast30Days: int


class GetVenueOffersStatsModel(HttpBodyModel):
    venueId: int
    totalViews6Months: int
    topOffersByConsultation: list[TopOffersByConsultationModel]


class GetOffererNameResponseModel(HttpBodyModel):
    id: int
    name: str


class GetOfferersNamesResponseModel(HttpBodyModel):
    offerers_names: list[GetOffererNameResponseModel]
