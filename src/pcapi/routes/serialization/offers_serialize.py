from datetime import datetime
from typing import Any
from typing import List
from typing import Optional
from typing import Union

from pydantic import BaseModel
from pydantic import validator

from pcapi.serialization.utils import cast_optional_field_str_to_int
from pcapi.serialization.utils import dehumanize_field
from pcapi.serialization.utils import dehumanize_list_field
from pcapi.serialization.utils import humanize_field
from pcapi.serialization.utils import to_camel
from pcapi.utils.cancellation_date import get_cancellation_limit_date
from pcapi.utils.date import format_into_utc_date
from pcapi.validation.routes.offers import check_offer_name_length_is_valid
from pcapi.validation.routes.offers import check_offer_type_is_valid


class PostOfferBodyModel(BaseModel):
    venue_id: str
    product_id: Optional[int]
    type: Optional[str]
    name: Optional[str]
    booking_email: Optional[str]
    url: Optional[str]
    media_urls: Optional[List[str]]
    description: Optional[str]
    withdrawal_details: Optional[str]
    conditions: Optional[str]
    age_min: Optional[int]
    age_max: Optional[int]
    duration_minutes: Optional[int]
    is_national: Optional[bool]
    is_duo: Optional[bool]

    _dehumanize_product_id = dehumanize_field("product_id")

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

    class Config:
        alias_generator = to_camel


class PatchOfferBodyModel(BaseModel):
    bookingEmail: Optional[str]
    description: Optional[str]
    isNational: Optional[bool]
    name: Optional[str]
    extraData: Any
    type: Optional[str]
    url: Optional[str]
    withdrawalDetails: Optional[str]
    isActive: Optional[bool]
    isDuo: Optional[bool]
    durationMinutes: Optional[int]
    mediaUrls: Optional[List[str]]
    ageMin: Optional[int]
    ageMax: Optional[int]
    conditions: Optional[str]
    venueId: Optional[str]
    productId: Optional[str]

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
    ids: List[int]

    _dehumanize_ids = dehumanize_list_field("ids")

    class Config:
        alias_generator = to_camel


class ListOffersVenueResponseModel(BaseModel):
    id: str
    isVirtual: bool
    managingOffererId: str
    name: str
    offererName: str
    publicName: Optional[str]


class ListOffersStockResponseModel(BaseModel):
    id: str
    offerId: str
    remainingQuantity: Union[int, str]

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
    stocks: List[ListOffersStockResponseModel]
    thumbUrl: Optional[str]
    type: str
    venue: ListOffersVenueResponseModel
    venueId: str


class ListOffersResponseModel(BaseModel):
    offers: List[ListOffersOfferResponseModel]
    page: int
    page_count: int
    total_count: int


class ListOffersQueryModel(BaseModel):
    paginate: Optional[int]
    page: Optional[int]
    name: Optional[str]
    offerer_id: Optional[int]
    status: Optional[str]
    venue_id: Optional[int]
    type_id: Optional[str]
    creation_mode: Optional[str]

    _cast_paginate = cast_optional_field_str_to_int("paginate")
    _cast_page = cast_optional_field_str_to_int("page")
    _dehumanize_venue_id = dehumanize_field("venue_id")
    _dehumanize_offerer_id = dehumanize_field("offerer_id")

    class Config:
        alias_generator = to_camel
        extra = "forbid"
        arbitrary_types_allowed = True


class GetOfferOfferTypeResponseModel(BaseModel):
    appLabel: str
    conditionalFields: List[Optional[str]]
    description: str
    isActive: bool
    offlineOnly: bool
    onlineOnly: bool
    proLabel: str
    sublabel: str
    type: str
    value: str


class GetOfferProductResponseModel(BaseModel):
    ageMax: Optional[int]
    ageMin: Optional[int]
    conditions: Optional[str]
    dateModifiedAtLastProvider: Optional[str]
    description: Optional[str]
    durationMinutes: Optional[int]
    extraData: Any
    fieldsUpdated: List[str]
    id: str
    idAtProviders: Optional[str]
    isGcuCompatible: bool
    isNational: bool
    lastProviderId: Optional[str]
    mediaUrls: List[str]
    name: str
    owningOffererId: Optional[str]
    thumbCount: int
    url: Optional[str]


class GetOfferStockResponseModel(BaseModel):
    beginningDatetime: Optional[str]
    bookingLimitDatetime: Optional[str]
    bookingsQuantity: int
    cancellationLimitDate: Optional[str]
    dateCreated: str
    dateModified: str
    dateModifiedAtLastProvider: Optional[str]
    fieldsUpdated: List[str]
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

    @validator("cancellationLimitDate", pre=True, always=True)
    def validate_cancellation_limit_date(cls, cancellation_limit_date, values):
        return get_cancellation_limit_date(values.get("beginningDatetime"), cancellation_limit_date)


class GetOfferManagingOffererResponseModel(BaseModel):
    address: Optional[str]
    bic: Optional[str]
    city: str
    dateCreated: str
    dateModifiedAtLastProvider: Optional[str]
    fieldsUpdated: List[str]
    iban: Optional[str]
    id: str
    idAtProviders: Optional[str]
    isActive: bool
    isValidated: bool
    lastProviderId: Optional[str]
    name: str
    postalCode: str
    siren: str
    thumbCount: int


class GetOfferVenueResponseModel(BaseModel):
    address: Optional[str]
    bic: Optional[str]
    bookingEmail: Optional[str]
    city: Optional[str]
    comment: Optional[str]
    dateCreated: Optional[str]
    dateModifiedAtLastProvider: Optional[str]
    departementCode: Optional[str]
    fieldsUpdated: List[str]
    iban: Optional[str]
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


class GetOfferLastProviderResponseModel(BaseModel):
    apiKey: Optional[str]
    apiKeyGenerationDate: Optional[str]
    enabledForPro: bool
    id: str
    isActive: bool
    localClass: str
    name: str
    requireProviderIdentifier: bool


class GetOfferMediationResponseModel(BaseModel):
    authorId: Optional[str]
    credit: Optional[str]
    dateCreated: str
    dateModifiedAtLastProvider: Optional[str]
    fieldsUpdated: List[str]
    id: str
    idAtProviders: Optional[str]
    isActive: bool
    lastProviderId: Optional[str]
    offerId: str
    thumbCount: int
    thumbUrl: Optional[str]


class GetOfferResponseModel(BaseModel):
    activeMediation: Optional[GetOfferMediationResponseModel]
    ageMax: Optional[int]
    ageMin: Optional[int]
    bookingEmail: Optional[str]
    conditions: Optional[str]
    dateCreated: str
    dateModifiedAtLastProvider: Optional[str]
    description: Optional[str]
    durationMinutes: Optional[int]
    extraData: Any
    fieldsUpdated: List[str]
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
    lastProvider: Optional[GetOfferLastProviderResponseModel]
    lastProviderId: Optional[str]
    mediaUrls: List[str]
    mediations: List[GetOfferMediationResponseModel]
    name: str
    offerType: GetOfferOfferTypeResponseModel
    product: GetOfferProductResponseModel
    productId: str
    stocks: List[GetOfferStockResponseModel]
    thumbUrl: Optional[str]
    type: str
    url: Optional[str]
    venue: GetOfferVenueResponseModel
    venueId: str
    withdrawalDetails: Optional[str]

    class Config:
        json_encoders = {datetime: format_into_utc_date}
