from datetime import datetime
from typing import Any
from typing import Optional
from typing import Union

from pydantic import BaseModel
from pydantic import Field
from pydantic import HttpUrl
from pydantic import validator

from pcapi.core.bookings.api import compute_confirmation_date
from pcapi.core.offers import repository as offers_repository
from pcapi.core.offers.models import OfferStatus
from pcapi.models import ThingType
from pcapi.models.feature import FeatureToggle
from pcapi.repository import feature_queries
from pcapi.serialization.utils import cast_optional_field_str_to_int
from pcapi.serialization.utils import dehumanize_field
from pcapi.serialization.utils import dehumanize_list_field
from pcapi.serialization.utils import humanize_field
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import DateTimes
from pcapi.utils.date import format_into_utc_date
from pcapi.validation.routes.offers import check_offer_isbn_is_valid
from pcapi.validation.routes.offers import check_offer_name_length_is_valid
from pcapi.validation.routes.offers import check_offer_type_is_valid


class PostOfferBodyModel(BaseModel):
    venue_id: str
    product_id: Optional[str]
    type: Optional[str]
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

    @validator("type", pre=True)
    def validate_type(cls, type_field, values):  # pylint: disable=no-self-argument
        if not values["product_id"]:
            check_offer_type_is_valid(type_field)
        return type_field

    @validator("extra_data", pre=True)
    def validate_isbn(cls, extra_data_field, values):  # pylint: disable=no-self-argument
        if (
            feature_queries.is_active(FeatureToggle.ENABLE_ISBN_REQUIRED_IN_LIVRE_EDITION_OFFER_CREATION)
            and not values["product_id"]
            and values["type"] == str(ThingType.LIVRE_EDITION)
        ):
            check_offer_isbn_is_valid(extra_data_field["isbn"])
        return extra_data_field

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class PatchOfferBodyModel(BaseModel):
    bookingEmail: Optional[str]
    description: Optional[str]
    isNational: Optional[bool]
    name: Optional[str]
    extraData: Any
    type: Optional[str]
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

    @validator("name", pre=True)
    def validate_name(cls, name):  # pylint: disable=no-self-argument
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
    name: Optional[str]
    type_id: Optional[str]
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
    name: str
    stocks: list[ListOffersStockResponseModel]
    thumbUrl: Optional[str]
    productIsbn: Optional[str]
    type: str
    venue: ListOffersVenueResponseModel
    status: str
    venueId: str


class ListOffersResponseModel(BaseModel):
    offers: list[ListOffersOfferResponseModel]

    class Config:
        json_encoders = {datetime: format_into_utc_date}


class ListOffersQueryModel(BaseModel):
    name: Optional[str]
    offerer_id: Optional[int]
    status: Optional[str]
    venue_id: Optional[int]
    type_id: Optional[str]
    creation_mode: Optional[str]
    period_beginning_date: Optional[str]
    period_ending_date: Optional[str]

    _dehumanize_venue_id = dehumanize_field("venue_id")
    _dehumanize_offerer_id = dehumanize_field("offerer_id")

    class Config:
        alias_generator = to_camel
        extra = "forbid"
        arbitrary_types_allowed = True


class GetOfferOfferTypeResponseModel(BaseModel):
    appLabel: str
    canExpire: Optional[bool]
    conditionalFields: list[Optional[str]]
    description: str
    isActive: bool
    offlineOnly: bool
    onlineOnly: bool
    proLabel: str
    sublabel: str
    type: str
    value: str

    class Config:
        orm_mode = True


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
    def from_orm(cls, stock):  # type: ignore
        stock.hasActivationCode = offers_repository.get_available_activation_code(stock) is not None
        return super().from_orm(stock)

    @validator("cancellationLimitDate", pre=True, always=True)
    def validate_cancellation_limit_date(cls, cancellation_limit_date, values):  # pylint: disable=no-self-argument
        return compute_confirmation_date(values.get("beginningDatetime"), datetime.now())

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
    venueTypeId: Optional[str]

    _humanize_id = humanize_field("id")
    _humanize_managing_offerer_id = humanize_field("managingOffererId")
    _humanize_last_provider_id = humanize_field("lastProviderId")
    _humanize_venue_label_id = humanize_field("venueLabelId")
    _humanize_venue_type_id = humanize_field("venueTypeId")

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
    idAtProviders: Optional[str]
    isActive: bool
    isBookable: bool
    isDigital: bool
    isDuo: bool
    isEditable: bool
    isEvent: bool
    isNational: bool
    isThing: bool
    audioDisabilityCompliant: Optional[bool]
    mentalDisabilityCompliant: Optional[bool]
    motorDisabilityCompliant: Optional[bool]
    visualDisabilityCompliant: Optional[bool]
    lastProvider: Optional[GetOfferLastProviderResponseModel]
    lastProviderId: Optional[str]
    mediaUrls: list[str]
    mediations: list[GetOfferMediationResponseModel]
    name: str
    offerType: GetOfferOfferTypeResponseModel
    product: GetOfferProductResponseModel
    productId: str
    stocks: list[GetOfferStockResponseModel]
    thumbUrl: Optional[str]
    type: str
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

    class Config:
        orm_mode = True
        json_encoders = {datetime: format_into_utc_date}
        use_enum_values = True


class ImageBodyModel(BaseModel):
    url: str


class ImageResponseModel(BaseModel):
    errors: Optional[list[str]]
    image: Optional[str]


class SubCategoryResponseModel(BaseModel):
    id: int
    name: str
    categoryId: int
    isEvent: bool
    isDigital: bool
    isDigitalDeposit: bool
    isPhysicalDeposit: bool
    proLabel: str
    appLabel: str
    conditionalFields: Optional[list[str]]
    canExpire: bool
    canBeDuo: bool

    class Config:
        orm_mode = True


class CategoryResponseModel(BaseModel):
    id: int
    name: str
    proLabel: str
    appLabel: str

    class Config:
        orm_mode = True


class CategoriesResponseModel(BaseModel):
    categories: list[CategoryResponseModel]
    sub_categories: list[SubCategoryResponseModel]
