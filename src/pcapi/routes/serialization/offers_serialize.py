from typing import Dict, Optional, List, Union
from pydantic import BaseModel, validator

from pcapi.models import OfferSQLEntity, UserSQLEntity
from pcapi.core.bookings.repository import find_first_matching_from_offer_by_user
from pcapi.routes.serialization.dictifier import as_dict
from pcapi.utils.includes import (
    OFFER_INCLUDES,
    WEBAPP_GET_BOOKING_WITH_QR_CODE_INCLUDES,
)
from pcapi.serialization.utils import (
    to_camel,
    dehumanize_field,
    humanize_field,
    dehumanize_list_field,
    cast_optional_field_str_to_int,
)
from pcapi.validation.routes.offers import (
    check_offer_name_length_is_valid,
    check_offer_type_is_valid,
)


def serialize_offer(offer: OfferSQLEntity, current_user: UserSQLEntity) -> Dict:
    dict_offer = as_dict(offer, includes=OFFER_INCLUDES)

    booking = find_first_matching_from_offer_by_user(offer.id, current_user.id)
    if booking:
        dict_offer["firstMatchingBooking"] = as_dict(
            booking, includes=WEBAPP_GET_BOOKING_WITH_QR_CODE_INCLUDES
        )

    return dict_offer


class PostOfferBodyModel(BaseModel):
    venue_id: str
    product_id: Optional[int]
    type: Optional[str]
    name: Optional[str]
    booking_email: Optional[str]

    _dehumanize_product_id = dehumanize_field("product_id")

    @validator("name", pre=True)
    def validate_name(cls, name, values):
        if not values["product_id"]:
            check_offer_name_length_is_valid(name)
        return name

    @validator("type", pre=True)
    def validate_type(cls, type_field, values):
        if not values["product_id"]:
            check_offer_type_is_valid(type_field)
        return type_field

    class Config:
        alias_generator = to_camel


class ExtraDataModel(BaseModel):
    author: Optional[str]
    musicSubType: Optional[str]
    musicType: Optional[str]
    performer: Optional[str]


class PatchOfferBodyModel(BaseModel):
    bookingEmail: Optional[str]
    description: Optional[str]
    isNational: Optional[bool]
    name: Optional[str]
    extraData: Optional[ExtraDataModel]
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
    def validate_name(cls, name):
        if name:
            check_offer_name_length_is_valid(name)
        return name

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class OfferResponseIdModel(BaseModel):
    id: str

    _humanize_id = humanize_field("id")

    class Config:  # pylint: disable=too-few-public-methods
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
    remainingQuantity: Union[str, int]


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
    active: Optional[str]
    inactive: Optional[str]
    paginate: Optional[int]
    page: Optional[int]
    name: Optional[str]
    offerer_id: Optional[int]
    venue_id: Optional[int]

    _cast_paginate = cast_optional_field_str_to_int("paginate")
    _cast_page = cast_optional_field_str_to_int("page")
    _dehumanize_venue_id = dehumanize_field("venue_id")
    _dehumanize_offerer_id = dehumanize_field("offerer_id")

    class Config:
        alias_generator = to_camel
        extra = "forbid"
        arbitrary_types_allowed = True
