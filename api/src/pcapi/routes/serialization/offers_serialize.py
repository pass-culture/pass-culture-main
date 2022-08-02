from datetime import datetime
import enum
from typing import Any

from pydantic import Field
from pydantic import HttpUrl
from pydantic import validator

from pcapi.core.bookings.api import compute_cancellation_limit_date
from pcapi.core.categories.conf import can_create_from_isbn
from pcapi.core.categories.subcategories import SubcategoryIdEnum
from pcapi.core.offers import repository as offers_repository
from pcapi.core.offers.models import Stock
from pcapi.core.offers.models import WithdrawalTypeEnum
from pcapi.models.feature import FeatureToggle
from pcapi.models.offer_mixin import OfferStatus
from pcapi.routes.native.v1.serialization.common_models import AccessibilityComplianceMixin
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import dehumanize_field
from pcapi.serialization.utils import dehumanize_list_field
from pcapi.serialization.utils import humanize_field
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import DateTimes
from pcapi.utils.date import format_into_utc_date
from pcapi.validation.routes.offers import check_offer_isbn_is_valid
from pcapi.validation.routes.offers import check_offer_name_length_is_valid


class SubcategoryResponseModel(BaseModel):
    id: str
    category_id: str
    pro_label: str
    app_label: str
    search_group_name: str | None
    is_event: bool
    conditional_fields: list[str]
    can_expire: bool
    can_be_duo: bool
    can_be_educational: bool
    online_offline_platform: str
    is_digital_deposit: bool
    is_physical_deposit: bool
    reimbursement_rule: str
    is_selectable: bool

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        orm_mode = True


class CategoryResponseModel(BaseModel):
    id: str
    pro_label: str
    is_selectable: bool

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        orm_mode = True


class PostOfferBodyModel(BaseModel):
    venue_id: str
    product_id: str | None
    subcategory_id: str
    # FIXME (cgaunet, 2022-08-02): This field should not be nullable
    name: str | None
    booking_email: str | None
    external_ticket_office_url: HttpUrl | None
    url: HttpUrl | None
    media_urls: list[str] | None
    description: str | None
    withdrawal_details: str | None
    withdrawal_type: WithdrawalTypeEnum | None
    withdrawal_delay: int | None
    conditions: str | None
    age_min: int | None
    age_max: int | None
    duration_minutes: int | None
    is_national: bool | None
    is_duo: bool | None
    is_educational: bool | None
    # TODO (schable, 2021-01-14): remove the default value for the 4 following accessibility fields
    #  when new offer creation will be activated in pro app (current offer creation does not send those fields)
    audio_disability_compliant: bool = False
    mental_disability_compliant: bool = False
    motor_disability_compliant: bool = False
    visual_disability_compliant: bool = False
    extra_data: Any
    # FIXME (viconnex, 2020-12-02): this field is actually
    # unused for the offer creation. But the webapp does send it so
    # we must list them here.
    offererId: str | None

    @validator("name", pre=True)
    def validate_name(cls, name, values):  # type: ignore [no-untyped-def] # pylint: disable=no-self-argument
        if not values["product_id"]:
            check_offer_name_length_is_valid(name)
        return name

    @validator("extra_data", pre=True)
    def validate_isbn(cls, extra_data_field, values):  # type: ignore [no-untyped-def] # pylint: disable=no-self-argument
        if (
            FeatureToggle.ENABLE_ISBN_REQUIRED_IN_LIVRE_EDITION_OFFER_CREATION.is_active()
            and not values["product_id"]
            and can_create_from_isbn(subcategory_id=values["subcategory_id"])
        ):
            check_offer_isbn_is_valid(extra_data_field["isbn"])
        return extra_data_field

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class OfferAddressType(enum.Enum):
    OFFERER_VENUE = "offererVenue"
    SCHOOL = "school"
    OTHER = "other"


class PatchOfferBodyModel(BaseModel, AccessibilityComplianceMixin):
    bookingEmail: str | None
    description: str | None
    isNational: bool | None
    name: str | None
    extraData: Any
    externalTicketOfficeUrl: HttpUrl | None
    url: HttpUrl | None
    withdrawalDetails: str | None
    withdrawalType: WithdrawalTypeEnum | None
    withdrawalDelay: int | None
    isActive: bool | None
    isDuo: bool | None
    durationMinutes: int | None
    mediaUrls: list[str] | None
    ageMin: int | None
    ageMax: int | None
    conditions: str | None
    venueId: str | None
    productId: str | None

    @validator("name", pre=True, allow_reuse=True)
    def validate_name(cls, name):  # type: ignore [no-untyped-def] # pylint: disable=no-self-argument
        if name:
            check_offer_name_length_is_valid(name)
        return name

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class OfferResponseIdModel(BaseModel):
    id: str

    _humanize_id = humanize_field("id")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class PatchOfferPublishBodyModel(BaseModel):
    id: int
    _dehumanize_id = dehumanize_field("id")


class PatchOfferActiveStatusBodyModel(BaseModel):
    is_active: bool
    ids: list[int]

    _dehumanize_ids = dehumanize_list_field("ids")

    class Config:
        alias_generator = to_camel


class PatchAllOffersActiveStatusBodyModel(BaseModel):
    is_active: bool
    offerer_id: int | None
    venue_id: int | None
    name_or_isbn: str | None
    category_id: str | None
    creation_mode: str | None
    status: str | None
    period_beginning_date: datetime | None
    period_ending_date: datetime | None

    _dehumanize_offerer_id = dehumanize_field("offerer_id")
    _dehumanize_venue_id = dehumanize_field("venue_id")

    class Config:
        alias_generator = to_camel


class PatchAllOffersActiveStatusResponseModel(BaseModel):
    pass


class ListOffersVenueResponseModel(BaseModel):
    id: str
    isVirtual: bool
    managingOffererId: str
    name: str
    offererName: str
    publicName: str | None
    departementCode: str | None


class ListOffersStockResponseModel(BaseModel):
    id: str
    hasBookingLimitDatetimePassed: bool
    offerId: str
    remainingQuantity: int | str
    beginningDatetime: datetime | None

    @validator("remainingQuantity", pre=True)
    def validate_remaining_quantity(cls, remainingQuantity):  # type: ignore [no-untyped-def] # pylint: disable=no-self-argument
        if remainingQuantity and remainingQuantity != "0" and not isinstance(remainingQuantity, int):
            return remainingQuantity.lstrip("0")
        return remainingQuantity


class ListOffersOfferResponseModel(BaseModel):
    hasBookingLimitDatetimesPassed: bool
    id: str
    isActive: bool
    isEditable: bool
    isEvent: bool
    isThing: bool
    isEducational: bool
    name: str
    stocks: list[ListOffersStockResponseModel]
    thumbUrl: str | None
    productIsbn: str | None
    subcategoryId: SubcategoryIdEnum
    venue: ListOffersVenueResponseModel
    status: str
    venueId: str
    isShowcase: bool | None


class ListOffersResponseModel(BaseModel):
    __root__: list[ListOffersOfferResponseModel]

    class Config:
        json_encoders = {datetime: format_into_utc_date}


class ListOffersQueryModel(BaseModel):
    nameOrIsbn: str | None
    offerer_id: int | None
    status: str | None
    venue_id: int | None
    categoryId: str | None
    creation_mode: str | None
    period_beginning_date: str | None
    period_ending_date: str | None

    _dehumanize_venue_id = dehumanize_field("venue_id")
    _dehumanize_offerer_id = dehumanize_field("offerer_id")

    class Config:
        alias_generator = to_camel
        extra = "forbid"
        arbitrary_types_allowed = True


class GetOfferProductResponseModel(BaseModel):
    ageMax: int | None
    ageMin: int | None
    conditions: str | None
    dateModifiedAtLastProvider: datetime | None
    description: str | None
    durationMinutes: int | None
    extraData: Any
    fieldsUpdated: list[str]
    id: str
    idAtProviders: str | None
    isGcuCompatible: bool
    isNational: bool
    lastProviderId: str | None
    mediaUrls: list[str]
    name: str
    owningOffererId: str | None
    thumbCount: int
    url: str | None

    _humanize_id = humanize_field("id")
    _humanize_last_provider_id = humanize_field("lastProviderId")
    _humanize_owning_offerer_id = humanize_field("owningOffererId")

    class Config:
        orm_mode = True
        json_encoders = {datetime: format_into_utc_date}


class GetOfferStockResponseModel(BaseModel):
    beginningDatetime: datetime | None
    bookingLimitDatetime: datetime | None
    dnBookedQuantity: int = Field(alias="bookingsQuantity")
    cancellationLimitDate: datetime | None
    dateCreated: datetime
    dateModified: datetime
    dateModifiedAtLastProvider: datetime | None
    fieldsUpdated: list[str]
    hasActivationCode: bool
    id: str
    idAtProviders: str | None
    isBookable: bool
    isEventDeletable: bool
    isEventExpired: bool
    isSoftDeleted: bool
    lastProviderId: str | None
    offerId: str
    price: float
    quantity: int | None
    remainingQuantity: int | str | None

    _humanize_id = humanize_field("id")
    _humanize_last_provider_id = humanize_field("lastProviderId")
    _humanize_offer_id = humanize_field("offerId")

    @classmethod
    def from_orm(cls, stock: Stock):  # type: ignore
        # here we have N+1 requests (for each stock we query an activation code)
        # but it should be more efficient than loading all activationCodes of all stocks
        stock.hasActivationCode = (
            stock.canHaveActivationCodes and offers_repository.get_available_activation_code(stock) is not None
        )
        return super().from_orm(stock)

    @validator("cancellationLimitDate", pre=True, always=True)
    def validate_cancellation_limit_date(cls, cancellation_limit_date, values):  # type: ignore [no-untyped-def] # pylint: disable=no-self-argument
        return compute_cancellation_limit_date(values.get("beginningDatetime"), datetime.utcnow())

    class Config:
        allow_population_by_field_name = True
        orm_mode = True
        json_encoders = {datetime: format_into_utc_date}


class GetOfferManagingOffererResponseModel(BaseModel):
    address: str | None
    city: str
    dateCreated: datetime
    dateModifiedAtLastProvider: datetime | None
    fieldsUpdated: list[str]
    id: str
    idAtProviders: str | None
    isActive: bool
    isValidated: bool
    lastProviderId: str | None
    name: str
    postalCode: str
    # FIXME (dbaty, 2020-11-09): optional until we populate the database (PC-5693)
    siren: str | None
    thumbCount: int

    _humanize_id = humanize_field("id")
    _humanize_last_provider_id = humanize_field("lastProviderId")

    class Config:
        orm_mode = True


class GetOfferVenueResponseModel(BaseModel, AccessibilityComplianceMixin):
    address: str | None
    bookingEmail: str | None
    city: str | None
    comment: str | None
    dateCreated: datetime | None
    dateModifiedAtLastProvider: datetime | None
    departementCode: str | None
    fieldsUpdated: list[str]
    id: str
    idAtProviders: str | None
    isValidated: bool
    isVirtual: bool
    lastProviderId: str | None
    latitude: float | None
    longitude: float | None
    managingOfferer: GetOfferManagingOffererResponseModel
    managingOffererId: str
    name: str
    postalCode: str | None
    publicName: str | None
    siret: str | None
    thumbCount: int
    venueLabelId: str | None

    _humanize_id = humanize_field("id")
    _humanize_managing_offerer_id = humanize_field("managingOffererId")
    _humanize_last_provider_id = humanize_field("lastProviderId")
    _humanize_venue_label_id = humanize_field("venueLabelId")

    class Config:
        orm_mode = True
        json_encoders = {datetime: format_into_utc_date}


# FIXME (apibrac, 2021-03-23): we should not expose so much information to the fronts.
# Only the name is needed in pro and nothing in webapp => can we just send a providerName field?
# The field lastProviderId is not used anywhere in the fronts either.
class GetOfferLastProviderResponseModel(BaseModel):
    enabledForPro: bool
    id: str
    isActive: bool
    localClass: str | None
    name: str

    _humanize_id = humanize_field("id")

    class Config:
        orm_mode = True


class GetOfferMediationResponseModel(BaseModel):
    authorId: str | None
    credit: str | None
    dateCreated: datetime
    dateModifiedAtLastProvider: datetime | None
    fieldsUpdated: list[str]
    id: str
    idAtProviders: str | None
    isActive: bool
    lastProviderId: str | None
    offerId: str
    thumbCount: int
    thumbUrl: str | None

    _humanize_id = humanize_field("id")
    _humanize_offer_id = humanize_field("offerId")
    _humanize_last_provider_id = humanize_field("lastProviderId")

    class Config:
        orm_mode = True
        json_encoders = {datetime: format_into_utc_date}


class GetOfferResponseModel(BaseModel, AccessibilityComplianceMixin):
    activeMediation: GetOfferMediationResponseModel | None
    ageMax: int | None
    ageMin: int | None
    bookingEmail: str | None
    conditions: str | None
    dateCreated: datetime
    dateModifiedAtLastProvider: datetime | None
    dateRange: list[datetime]
    description: str | None
    durationMinutes: int | None
    extraData: Any
    fieldsUpdated: list[str]
    hasBookingLimitDatetimesPassed: bool
    id: str
    isActive: bool
    isBookable: bool
    isDigital: bool
    isDuo: bool
    isEditable: bool
    isEducational: bool
    isEvent: bool
    isNational: bool
    isThing: bool
    nonHumanizedId: int
    lastProvider: GetOfferLastProviderResponseModel | None
    lastProviderId: str | None
    mediaUrls: list[str]
    mediations: list[GetOfferMediationResponseModel]
    name: str
    product: GetOfferProductResponseModel
    productId: str
    stocks: list[GetOfferStockResponseModel]
    subcategoryId: SubcategoryIdEnum
    thumbUrl: str | None
    externalTicketOfficeUrl: str | None
    url: str | None
    venue: GetOfferVenueResponseModel
    venueId: str
    withdrawalDetails: str | None
    status: OfferStatus

    _humanize_id = humanize_field("id")
    _humanize_product_id = humanize_field("productId")
    _humanize_venue_id = humanize_field("venueId")
    _humanize_last_provider_id = humanize_field("lastProviderId")

    @validator("dateRange", pre=True)
    def extract_datetime_list_from_DateTimes_type(  # pylint: disable=no-self-argument
        cls, date_range: DateTimes
    ) -> list[datetime]:
        if isinstance(date_range, DateTimes):
            return date_range.datetimes
        return date_range

    @classmethod
    def from_orm(cls, offer):  # type: ignore
        offer.nonHumanizedId = offer.id
        return super().from_orm(offer)

    class Config:
        orm_mode = True
        json_encoders = {datetime: format_into_utc_date}
        use_enum_values = True


class GetIndividualOfferResponseModel(GetOfferResponseModel):
    withdrawalType: WithdrawalTypeEnum | None
    withdrawalDelay: int | None


class ImageBodyModel(BaseModel):
    url: str


class CategoriesResponseModel(BaseModel):
    categories: list[CategoryResponseModel]
    subcategories: list[SubcategoryResponseModel]
