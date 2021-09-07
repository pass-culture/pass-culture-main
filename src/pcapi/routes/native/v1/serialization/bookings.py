from datetime import datetime
from typing import Any
from typing import Optional

from pydantic.class_validators import validator

from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingCancellationReasons
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import Offer
from pcapi.routes.native.utils import convert_to_cent
from pcapi.routes.native.v1.serialization.common_models import Coordinates
from pcapi.routes.native.v1.serialization.offers import OfferCategoryResponse
from pcapi.routes.native.v1.serialization.offers import OfferImageResponse
from pcapi.routes.native.v1.serialization.offers import get_serialized_offer_category
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import format_into_utc_date

from . import BaseModel


class BookOfferRequest(BaseModel):
    stock_id: int
    quantity: int

    class Config:
        alias_generator = to_camel


class BookOfferResponse(BaseModel):
    bookingId: int


class BookingVenueResponse(BaseModel):
    id: int
    city: Optional[str]
    name: str
    publicName: Optional[str]
    coordinates: Coordinates

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

    @classmethod
    def from_orm(cls: Any, venue: Venue):  # type: ignore
        venue.coordinates = {"latitude": venue.latitude, "longitude": venue.longitude}
        return super().from_orm(venue)


class BookingOfferExtraData(BaseModel):
    isbn: Optional[str]


class BookingOfferResponse(BaseModel):
    id: int
    name: str
    category: OfferCategoryResponse
    subcategoryId: str
    extraData: Optional[BookingOfferExtraData]
    image: Optional[OfferImageResponse]
    isDigital: bool
    isPermanent: bool
    url: Optional[str]
    venue: BookingVenueResponse
    withdrawalDetails: Optional[str]

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls: Any, offer: Offer):  # type: ignore
        offer.category = get_serialized_offer_category(offer)
        return super().from_orm(offer)


class BookingStockResponse(BaseModel):
    id: int
    beginningDatetime: Optional[datetime]
    offer: BookingOfferResponse

    class Config:
        orm_mode = True


class BookingActivationCodeResponse(BaseModel):
    code: str
    expirationDate: Optional[datetime]

    class Config:
        orm_mode = True


class BookingReponse(BaseModel):
    id: int
    cancellationDate: Optional[datetime]
    cancellationReason: Optional[BookingCancellationReasons]
    confirmationDate: Optional[datetime]
    completedUrl: Optional[str]
    dateUsed: Optional[datetime]
    expirationDate: Optional[datetime]
    qrCodeData: Optional[str]
    quantity: int
    stock: BookingStockResponse
    total_amount: int
    token: str
    activationCode: Optional[BookingActivationCodeResponse]

    _convert_total_amount = validator("total_amount", pre=True, allow_reuse=True)(convert_to_cent)

    @classmethod
    def from_orm(cls: Any, booking: Booking):  # type: ignore
        # Native application should use `booking.completedUrl` but actually
        # up to version 135, it uses booking.stock.offer.url instead.
        # Therefore the API will override `booking.stock.offer.url` with
        # `booking.completedUrl`.
        # Unfortunate side-effect, the offer object has its url modified and
        # needs to be rolledback.
        booking.stock.offer.url = booking.completedUrl
        booking.confirmationDate = booking.cancellationLimitDate
        return super().from_orm(booking)

    class Config:
        orm_mode = True
        alias_generator = to_camel
        allow_population_by_field_name = True


class BookingsResponse(BaseModel):
    ended_bookings: list[BookingReponse]
    ongoing_bookings: list[BookingReponse]

    class Config:
        json_encoders = {datetime: format_into_utc_date}


class BookingDisplayStatusRequest(BaseModel):
    ended: bool
