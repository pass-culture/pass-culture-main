from datetime import datetime
import enum
from typing import Any
from typing import Optional
from typing import Union

from pydantic import Field
from pydantic import HttpUrl
from pydantic import validator

from pcapi.core.bookings.api import compute_cancellation_limit_date
from pcapi.core.categories.conf import can_create_from_isbn
from pcapi.core.categories.subcategories import SubcategoryIdEnum
from pcapi.core.offers import repository as offers_repository
from pcapi.core.offers.models import Stock
from pcapi.models.feature import FeatureToggle
from pcapi.models.offer_mixin import OfferStatus
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
    search_group_name: Optional[str]
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
    product_id: Optional[str]
    subcategory_id: Optional[str]
    name: Optional[str]
    booking_email: Optional[str]
    external_ticket_office_url: Optional[HttpUrl]
    url: Optional[HttpUrl]
    media_urls: Optional[list[str]]
    description: Optional[str]
    withdrawal_details: Optional[str]
    conditions: Optional[str]
    age_min: Optional[int]
    age_max: Optional[int]
    duration_minutes: Optional[int]
    is_national: Optional[bool]
    is_duo: Optional[bool]
    is_educational: Optional[bool]
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
    offererId: Optional[str]

    @validator("name", pre=True)
    def validate_name(cls, name, values):  # pylint: disable=no-self-argument
        if not values["product_id"]:
            check_offer_name_length_is_valid(name)
        return name

    @validator("extra_data", pre=True)
    def validate_isbn(cls, extra_data_field, values):  # pylint: disable=no-self-argument
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


class EducationalOfferExtraDataOfferVenueBodyModel(BaseModel):
    addressType: OfferAddressType
    otherAddress: str
    venueId: str

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class PostEducationalOfferExtraDataBodyModel(BaseModel):
    students: list[str]
    offer_venue: EducationalOfferExtraDataOfferVenueBodyModel
    contact_email: str
    contact_phone: str

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class PostEducationalOfferBodyModel(BaseModel):
    offerer_id: str
    venue_id: str
    subcategory_id: str
    name: str
    booking_email: Optional[str]
    description: Optional[str]
    duration_minutes: Optional[int]
    audio_disability_compliant: bool = False
    mental_disability_compliant: bool = False
    motor_disability_compliant: bool = False
    visual_disability_compliant: bool = False
    extra_data: PostEducationalOfferExtraDataBodyModel

    @validator("name", pre=True)
    def validate_name(cls, name, values):  # pylint: disable=no-self-argument
        check_offer_name_length_is_valid(name)
        return name

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class EducationalOfferExtraDataBodyModel(PostEducationalOfferExtraDataBodyModel):
    is_showcase: bool = False


class EducationalOfferBodyModel(PostEducationalOfferBodyModel):
    extra_data: EducationalOfferExtraDataBodyModel


class CompletedEducationalOfferModel(EducationalOfferBodyModel):
    is_duo: bool = False
    is_educational: bool = True
    external_ticket_office_url: Optional[str] = None


class PatchOfferBodyModel(BaseModel):
    bookingEmail: Optional[str]
    description: Optional[str]
    isNational: Optional[bool]
    name: Optional[str]
    extraData: Any
    externalTicketOfficeUrl: Optional[HttpUrl]
    url: Optional[HttpUrl]
    withdrawalDetails: Optional[str]
    isActive: Optional[bool]
    isDuo: Optional[bool]
    durationMinutes: Optional[int]
    mediaUrls: Optional[list[str]]
    ageMin: Optional[int]
    ageMax: Optional[int]
    conditions: Optional[str]
    venueId: Optional[str]
    productId: Optional[str]
    audioDisabilityCompliant: Optional[bool]
    mentalDisabilityCompliant: Optional[bool]
    motorDisabilityCompliant: Optional[bool]
    visualDisabilityCompliant: Optional[bool]

    @validator("name", pre=True, allow_reuse=True)
    def validate_name(cls, name):  # pylint: disable=no-self-argument
        if name:
            check_offer_name_length_is_valid(name)
        return name

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class EducationalOfferPartialExtraDataBodyModel(BaseModel):
    students: Optional[list[str]]
    offerVenue: Optional[EducationalOfferExtraDataOfferVenueBodyModel]
    contactEmail: Optional[str]
    contactPhone: Optional[str]

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class PatchEducationalOfferBodyModel(BaseModel):
    bookingEmail: Optional[str]
    description: Optional[str]
    name: Optional[str]
    extraData: Optional[EducationalOfferPartialExtraDataBodyModel]
    durationMinutes: Optional[int]
    audioDisabilityCompliant: Optional[bool]
    mentalDisabilityCompliant: Optional[bool]
    motorDisabilityCompliant: Optional[bool]
    visualDisabilityCompliant: Optional[bool]
    subcategoryId: Optional[SubcategoryIdEnum]

    @validator("name", allow_reuse=True)
    def validate_name(cls, name):  # pylint: disable=no-self-argument
        assert name is not None and name.strip() != ""
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


class PatchOfferActiveStatusBodyModel(BaseModel):
    is_active: bool
    ids: list[int]

    _dehumanize_ids = dehumanize_list_field("ids")

    class Config:
        alias_generator = to_camel


class PatchAllOffersActiveStatusBodyModel(BaseModel):
    is_active: bool
    offerer_id: Optional[int]
    venue_id: Optional[int]
    name_or_isbn: Optional[str]
    category_id: Optional[str]
    creation_mode: Optional[str]
    status: Optional[str]
    period_beginning_date: Optional[datetime]
    period_ending_date: Optional[datetime]

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
    publicName: Optional[str]
    departementCode: Optional[str]


class ListOffersStockResponseModel(BaseModel):
    id: str
    hasBookingLimitDatetimePassed: bool
    offerId: str
    remainingQuantity: Union[int, str]
    beginningDatetime: Optional[datetime]

    @validator("remainingQuantity", pre=True)
    def validate_remaining_quantity(cls, remainingQuantity):  # pylint: disable=no-self-argument
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
    thumbUrl: Optional[str]
    productIsbn: Optional[str]
    subcategoryId: SubcategoryIdEnum
    venue: ListOffersVenueResponseModel
    status: str
    venueId: str
    isShowcase: Optional[bool]


class ListOffersResponseModel(BaseModel):
    __root__: list[ListOffersOfferResponseModel]

    class Config:
        json_encoders = {datetime: format_into_utc_date}


class ListOffersQueryModel(BaseModel):
    nameOrIsbn: Optional[str]
    offerer_id: Optional[int]
    status: Optional[str]
    venue_id: Optional[int]
    categoryId: Optional[str]
    creation_mode: Optional[str]
    period_beginning_date: Optional[str]
    period_ending_date: Optional[str]

    _dehumanize_venue_id = dehumanize_field("venue_id")
    _dehumanize_offerer_id = dehumanize_field("offerer_id")

    class Config:
        alias_generator = to_camel
        extra = "forbid"
        arbitrary_types_allowed = True


class GetOfferProductResponseModel(BaseModel):
    ageMax: Optional[int]
    ageMin: Optional[int]
    conditions: Optional[str]
    dateModifiedAtLastProvider: Optional[datetime]
    description: Optional[str]
    durationMinutes: Optional[int]
    extraData: Any
    fieldsUpdated: list[str]
    id: str
    idAtProviders: Optional[str]
    isGcuCompatible: bool
    isNational: bool
    lastProviderId: Optional[str]
    mediaUrls: list[str]
    name: str
    owningOffererId: Optional[str]
    thumbCount: int
    url: Optional[str]

    _humanize_id = humanize_field("id")
    _humanize_last_provider_id = humanize_field("lastProviderId")
    _humanize_owning_offerer_id = humanize_field("owningOffererId")

    class Config:
        orm_mode = True
        json_encoders = {datetime: format_into_utc_date}


class GetOfferStockResponseModel(BaseModel):
    beginningDatetime: Optional[datetime]
    bookingLimitDatetime: Optional[datetime]
    dnBookedQuantity: int = Field(alias="bookingsQuantity")
    cancellationLimitDate: Optional[datetime]
    dateCreated: datetime
    dateModified: datetime
    dateModifiedAtLastProvider: Optional[datetime]
    fieldsUpdated: list[str]
    hasActivationCode: bool
    id: str
    idAtProviders: Optional[str]
    isBookable: bool
    isEventDeletable: bool
    isEventExpired: bool
    isSoftDeleted: bool
    lastProviderId: Optional[str]
    offerId: str
    price: float
    quantity: Optional[int]
    remainingQuantity: Optional[Union[int, str]]

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
    def validate_cancellation_limit_date(cls, cancellation_limit_date, values):  # pylint: disable=no-self-argument
        return compute_cancellation_limit_date(values.get("beginningDatetime"), datetime.now())

    class Config:
        allow_population_by_field_name = True
        orm_mode = True
        json_encoders = {datetime: format_into_utc_date}


class GetOfferManagingOffererResponseModel(BaseModel):
    address: Optional[str]
    city: str
    dateCreated: datetime
    dateModifiedAtLastProvider: Optional[datetime]
    fieldsUpdated: list[str]
    id: str
    idAtProviders: Optional[str]
    isActive: bool
    isValidated: bool
    lastProviderId: Optional[str]
    name: str
    postalCode: str
    # FIXME (dbaty, 2020-11-09): optional until we populate the database (PC-5693)
    siren: Optional[str]
    thumbCount: int

    _humanize_id = humanize_field("id")
    _humanize_last_provider_id = humanize_field("lastProviderId")

    class Config:
        orm_mode = True


class GetOfferVenueResponseModel(BaseModel):
    address: Optional[str]
    bookingEmail: Optional[str]
    city: Optional[str]
    comment: Optional[str]
    dateCreated: Optional[datetime]
    dateModifiedAtLastProvider: Optional[datetime]
    departementCode: Optional[str]
    fieldsUpdated: list[str]
    id: str
    idAtProviders: Optional[str]
    isValidated: bool
    isVirtual: bool
    lastProviderId: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    managingOfferer: GetOfferManagingOffererResponseModel
    managingOffererId: str
    name: str
    postalCode: Optional[str]
    publicName: Optional[str]
    siret: Optional[str]
    thumbCount: int
    venueLabelId: Optional[str]
    audioDisabilityCompliant: Optional[bool]
    mentalDisabilityCompliant: Optional[bool]
    motorDisabilityCompliant: Optional[bool]
    visualDisabilityCompliant: Optional[bool]

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
    localClass: Optional[str]
    name: str

    _humanize_id = humanize_field("id")

    class Config:
        orm_mode = True


class GetOfferMediationResponseModel(BaseModel):
    authorId: Optional[str]
    credit: Optional[str]
    dateCreated: datetime
    dateModifiedAtLastProvider: Optional[datetime]
    fieldsUpdated: list[str]
    id: str
    idAtProviders: Optional[str]
    isActive: bool
    lastProviderId: Optional[str]
    offerId: str
    thumbCount: int
    thumbUrl: Optional[str]

    _humanize_id = humanize_field("id")
    _humanize_offer_id = humanize_field("offerId")
    _humanize_last_provider_id = humanize_field("lastProviderId")

    class Config:
        orm_mode = True
        json_encoders = {datetime: format_into_utc_date}


class GetOfferResponseModel(BaseModel):
    activeMediation: Optional[GetOfferMediationResponseModel]
    ageMax: Optional[int]
    ageMin: Optional[int]
    bookingEmail: Optional[str]
    conditions: Optional[str]
    dateCreated: datetime
    dateModifiedAtLastProvider: Optional[datetime]
    dateRange: list[datetime]
    description: Optional[str]
    durationMinutes: Optional[int]
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
    audioDisabilityCompliant: Optional[bool]
    mentalDisabilityCompliant: Optional[bool]
    motorDisabilityCompliant: Optional[bool]
    nonHumanizedId: int
    visualDisabilityCompliant: Optional[bool]
    lastProvider: Optional[GetOfferLastProviderResponseModel]
    lastProviderId: Optional[str]
    mediaUrls: list[str]
    mediations: list[GetOfferMediationResponseModel]
    name: str
    product: GetOfferProductResponseModel
    productId: str
    stocks: list[GetOfferStockResponseModel]
    subcategoryId: SubcategoryIdEnum
    thumbUrl: Optional[str]
    externalTicketOfficeUrl: Optional[str]
    url: Optional[str]
    venue: GetOfferVenueResponseModel
    venueId: str
    withdrawalDetails: Optional[str]
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


class ImageBodyModel(BaseModel):
    url: str


class CategoriesResponseModel(BaseModel):
    categories: list[CategoryResponseModel]
    subcategories: list[SubcategoryResponseModel]


class EducationalOfferShadowStockBodyModel(BaseModel):
    educational_price_detail: Optional[str]

    @validator("educational_price_detail")
    def validate_price_detail(cls, educational_price_detail):  # pylint: disable=no-self-argument
        if len(educational_price_detail) > 1000:
            raise ValueError("Le détail du prix ne doit pas excéder 1000 caractères.")
        return educational_price_detail

    class Config:
        alias_generator = to_camel
