from datetime import datetime
import enum
from typing import Any
from typing import Optional

from pydantic import BaseModel
from pydantic.class_validators import validator

from pcapi.core.bookings.models import BookingCancellationReasons
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import Offer
from pcapi.routes.native.utils import convert_to_cent
from pcapi.routes.native.v1.serialization.offers import OfferCategoryResponse
from pcapi.routes.native.v1.serialization.offers import OfferImageResponse
from pcapi.routes.native.v1.serialization.offers import get_serialized_offer_category
from pcapi.serialization.utils import to_camel


class PreBookingStatuses(enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    REFUSED = "REFUSED"
    DONE = "DONE"


class GetPreBookingsRequest(BaseModel):
    school_id: str
    year_id: str
    redactor_email: Optional[str]
    status: Optional[PreBookingStatuses]


class PreBookingVenueResponse(BaseModel):
    id: int
    address: Optional[str]
    city: Optional[str]
    name: str
    postalCode: Optional[str]
    publicName: Optional[str]

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

    @classmethod
    def from_orm(cls: Any, venue: Venue):  # type: ignore
        venue.coordinates = {"latitude": venue.latitude, "longitude": venue.longitude}
        return super().from_orm(venue)


class PreBookingOfferExtraData(BaseModel):
    isbn: Optional[str]


class PreBookingOfferResponse(BaseModel):
    id: int
    name: str
    category: OfferCategoryResponse
    extraData: Optional[PreBookingOfferExtraData]
    image: Optional[OfferImageResponse]
    isDigital: bool
    isPermanent: bool
    url: Optional[str]
    venue: PreBookingVenueResponse
    withdrawalDetails: Optional[str]

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls: Any, offer: Offer):  # type: ignore
        offer.category = get_serialized_offer_category(offer)
        return super().from_orm(offer)


class PreBookingStockResponse(BaseModel):
    id: int
    beginningDatetime: Optional[datetime]
    offer: PreBookingOfferResponse

    class Config:
        orm_mode = True


class PreBookingResponse(BaseModel):
    id: int
    cancellationDate: Optional[datetime]
    cancellationReason: Optional[BookingCancellationReasons]
    confirmationDate: Optional[datetime]
    confirmationLimitDate: Optional[datetime]
    expirationDate: Optional[datetime]
    quantity: int
    stock: PreBookingStockResponse
    total_amount: int

    _convert_total_amount = validator("total_amount", pre=True, allow_reuse=True)(convert_to_cent)

    class Config:
        orm_mode = True
        alias_generator = to_camel
        allow_population_by_field_name = True


class PreBookingsResponse(BaseModel):
    prebookings: list[PreBookingResponse]
