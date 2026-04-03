import enum
import typing
from datetime import date
from datetime import datetime
from typing import Iterable

import pydantic as pydantic_v2
import sqlalchemy.orm as sa_orm
from sqlalchemy.engine import Row

import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.models as offers_models
from pcapi.core.offerers import schemas as offerers_schemas
from pcapi.core.offerers.models import Target
from pcapi.models import db
from pcapi.routes.serialization import HttpBodyModel
from pcapi.routes.serialization import HttpQueryParamsModel
from pcapi.routes.serialization import address_serialize
from pcapi.routes.serialization import finance_serialize
from pcapi.routes.serialization import venue_collective_serialize
from pcapi.routes.serialization.venue_banners_serialize import BannerMetaModelV2
from pcapi.routes.shared import validation
from pcapi.serialization.exceptions import PydanticError
from pcapi.utils import phone_number as phone_number_utils
from pcapi.utils.email import sanitize_email


class GetOffererVenueResponseModel(HttpBodyModel):
    booking_email: str | None
    has_created_offer: bool
    has_adage_id: bool
    is_virtual: bool
    name: str
    id: int
    public_name: str
    siret: str | None
    activity: offerers_models.DisplayableActivity | None
    withdrawal_details: str | None
    collective_dms_applications: list[venue_collective_serialize.DMSApplicationForEACv2]
    has_partner_page: bool
    has_venue_providers: bool
    is_permanent: bool
    banner_url: str | None
    banner_meta: BannerMetaModelV2 | None

    @classmethod
    def build(
        cls,
        venue: offerers_models.Venue,
        ids_of_venues_with_offers: Iterable[int] = (),
    ) -> "GetOffererVenueResponseModel":
        activity = None
        if venue.activity and venue.activity != offerers_models.Activity.NOT_ASSIGNED:
            activity = offerers_models.DisplayableActivity[venue.activity.name]
        return cls(
            activity=activity,
            banner_meta=venue.bannerMeta,
            banner_url=venue.bannerUrl,
            booking_email=venue.bookingEmail,
            collective_dms_applications=[
                venue_collective_serialize.DMSApplicationForEACv2.build(application, venue.id)
                for application in venue.collectiveDmsApplications
            ],
            has_adage_id=bool(venue.adageId),
            has_created_offer=venue.id in ids_of_venues_with_offers,
            has_partner_page=venue._has_partner_page,
            has_venue_providers=bool(venue.venueProviders),
            id=venue.id,
            is_permanent=venue.isPermanent,
            is_virtual=venue.isVirtual,
            name=venue.name,
            public_name=venue.publicName,
            siret=venue.siret,
            withdrawal_details=venue.withdrawalDetails,
        )


# GetOffererResponseModel includes sensitive information and can be returned only if authenticated user has a validated
# access to the offerer. During subscription process, use PostOffererResponseModel
class GetOffererResponseModel(HttpBodyModel):
    has_available_pricing_points: bool
    has_digital_venue_at_least_one_offer: bool
    is_validated: bool
    is_active: bool
    managed_venues: list[GetOffererVenueResponseModel]
    name: str
    id: int
    siren: str
    has_valid_bank_account: bool
    has_pending_bank_account: bool
    has_non_free_offer: bool
    venues_with_non_free_offers_without_bank_accounts: list[int]
    has_active_offer: bool
    allowed_on_adage: bool
    has_bank_account_with_pending_corrections: bool
    is_onboarded: bool
    has_headline_offer: bool
    has_partner_page: bool
    is_caledonian: bool
    can_display_highlights: bool

    @classmethod
    def build(
        cls,
        row: Row,
        ids_of_venues_with_offers: Iterable[int],
        has_digital_venue_at_least_one_offer: bool,
        venues_with_non_free_offers_without_bank_accounts: list[int],
    ) -> typing.Self:
        offerer: offerers_models.Offerer = row.Offerer
        venues = (
            db.session.query(offerers_models.Venue)
            .filter_by(managingOffererId=offerer.id)
            .options(sa_orm.joinedload(offerers_models.Venue.collectiveDmsApplications))
            .options(sa_orm.joinedload(offerers_models.Venue.venueProviders))
            .options(sa_orm.joinedload(offerers_models.Venue.googlePlacesInfo))
            .order_by(offerers_models.Venue.publicName)
            .all()
        )

        return cls(
            allowed_on_adage=offerer.allowedOnAdage,
            can_display_highlights=row.canDisplayHighlights,
            has_active_offer=row.hasActiveOffer,
            has_available_pricing_points=any(venue.siret for venue in venues),
            has_bank_account_with_pending_corrections=row.hasBankAccountWithPendingCorrections,
            has_digital_venue_at_least_one_offer=has_digital_venue_at_least_one_offer,
            has_headline_offer=row.hasHeadlineOffer,
            has_non_free_offer=row.hasNonFreeOffer,
            has_partner_page=row.hasPartnerPage,
            has_pending_bank_account=row.hasPendingBankAccount,
            has_valid_bank_account=row.hasValidBankAccount,
            id=offerer.id,
            is_active=offerer.isActive and not offerer.isClosed,
            is_caledonian=offerer.is_caledonian,
            is_onboarded=row.isOnboarded,
            # Behavior in PC Pro for a closed offerer should be the same as for a suspended validated offerer
            is_validated=offerer.isValidated or offerer.isClosed,  # do now show "en attente de traitement"
            managed_venues=[GetOffererVenueResponseModel.build(venue, ids_of_venues_with_offers) for venue in venues],
            name=offerer.name,
            siren=offerer.siren,
            venues_with_non_free_offers_without_bank_accounts=venues_with_non_free_offers_without_bank_accounts,
        )


class GetOffererNameResponseModel(HttpBodyModel):
    id: int
    name: str


class OffererMemberStatus(enum.Enum):
    VALIDATED = "validated"
    PENDING = "pending"


class GetOffererMemberResponseModel(HttpBodyModel):
    email: str
    status: OffererMemberStatus


class GetOffererMembersResponseModel(HttpBodyModel):
    members: list[GetOffererMemberResponseModel]


class GetOfferersNamesResponseModel(HttpBodyModel):
    offerers_names: list[GetOffererNameResponseModel]
    offerers_names_with_pending_validation: list[GetOffererNameResponseModel]

    @classmethod
    def build(
        cls, offerers_names: Iterable, offerers_names_with_pending_validation: Iterable
    ) -> "GetOfferersNamesResponseModel":
        return cls(
            offerers_names=[GetOffererNameResponseModel(id=o.id, name=o.name) for o in offerers_names],
            offerers_names_with_pending_validation=[
                GetOffererNameResponseModel(id=o.id, name=o.name) for o in offerers_names_with_pending_validation
            ],
        )


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

    @classmethod
    def build(cls, offerer: offerers_models.Offerer) -> "GetEducationalOffererResponseModel":
        return cls(
            id=offerer.id,
            name=offerer.name,
            managedVenues=[
                GetEducationalOffererVenueResponseModel.build(venue)
                for venue in offerer.managedVenues
                if not venue.isSoftDeleted
                # We need to explicitly filter isSoftDeleted as the library does not filter them
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

    @pydantic_v2.field_validator("phone_number", mode="after")
    @classmethod
    def validate_field(cls, value: str | None) -> str | None:
        if value is None:
            return None

        try:
            parsed = phone_number_utils.parse_phone_number(value)
        except phone_number_utils.InvalidPhoneNumber:
            raise PydanticError("Ce numéro de telephone ne semble pas valide")

        return phone_number_utils.get_formatted_phone_number(parsed)


class SaveNewOnboardingDataQueryModel(HttpBodyModel):
    activity: offerers_models.ActivityOpenToPublic | offerers_models.ActivityNotOpenToPublic
    address: address_serialize.LocationBodyModelV2
    cultural_domains: list[str] | None = pydantic_v2.Field(min_length=1, default=None)
    create_venue_without_siret: bool = False
    is_open_to_public: bool
    public_name: str | None = None
    siret: str
    target: Target
    token: str
    web_presence: str
    phone_number: str | None = None

    @pydantic_v2.field_validator("phone_number", mode="after")
    def validate_phone_number(cls, phone_number: str | None) -> str | None:
        return validation.validate_nullable_phone_number(phone_number)


class InviteMemberQueryModel(HttpQueryParamsModel):
    email: str

    @pydantic_v2.field_validator("email")
    def validate_email(cls, email: str) -> str:
        try:
            return sanitize_email(email)
        except Exception as e:
            raise ValueError(email) from e


class GetOffererBankAccountsResponseModel(HttpBodyModel):
    id: int
    bank_accounts: list[finance_serialize.BankAccountResponseModel]
    managed_venues: list[finance_serialize.ManagedVenue]


class TopOffersResponseData(HttpBodyModel):
    offerId: int
    numberOfViews: int
    offerName: str
    image: offers_models.OfferImage | None
    isHeadlineOffer: bool


class OffererStatsDataModel(HttpBodyModel):
    totalViewsLast30Days: int
    topOffers: list[TopOffersResponseData]
    dailyViews: list[offerers_models.OffererViewsModel]


class GetOffererStatsResponseModel(HttpBodyModel):
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
    ) -> typing.Self:
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


class VenueDailyViewModel(HttpBodyModel):
    day: date
    views: int


class VenueStatsDataModel(HttpBodyModel):
    total_views_last_30_days: int
    top_offers: list[TopOffersResponseData]
    daily_views: list[VenueDailyViewModel]


class GetVenueStatsResponseModel(HttpBodyModel):
    venue_id: int
    json_data: VenueStatsDataModel


class LinkVenueToBankAccountBodyModel(HttpBodyModel):
    venues_ids: set[int]


class GetOffererV2StatsResponseModel(HttpBodyModel):
    published_public_offers: int
    published_educational_offers: int
    pending_public_offers: int
    pending_educational_offers: int


class GetOffererAddressResponseModel(HttpBodyModel):
    id: int
    label: str | None
    street: str | None
    postal_code: str
    city: str
    department_code: str | None


class GetOffererAddressesResponseModel(pydantic_v2.RootModel):
    root: list[GetOffererAddressResponseModel]


class GetOffererAddressesQueryModel(HttpQueryParamsModel):
    with_offers_option: offerers_schemas.GetOffererAddressesWithOffersOption | None = None


class OffererEligibilityResponseModel(HttpBodyModel):
    offerer_id: int
    has_adage_id: bool | None
    has_ds_application: bool | None
    is_onboarded: bool | None


class TopOffersByConsultationModel(HttpBodyModel):
    offerId: str
    totalViewsLast30Days: int


class GetVenueOffersStatsModel(HttpBodyModel):
    venueId: int
    totalViews6Months: int
    topOffersByConsultation: list[TopOffersByConsultationModel]
