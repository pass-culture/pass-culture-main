from datetime import datetime
from typing import Any

from pydantic.class_validators import validator

from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingCancellationReasons
from pcapi.core.categories.subcategories import SubcategoryIdEnum
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import WithdrawalTypeEnum
from pcapi.routes.native.utils import convert_to_cent
from pcapi.routes.native.v1.serialization.common_models import Coordinates
from pcapi.routes.native.v1.serialization.offers import OfferImageResponse
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import format_into_utc_date


class BookOfferRequest(BaseModel):
    stock_id: int
    quantity: int

    class Config:
        alias_generator = to_camel


class BookOfferResponse(BaseModel):
    bookingId: int


class BookingVenueResponse(BaseModel):
    id: int
    address: str | None
    postalCode: str | None
    city: str | None
    name: str
    publicName: str | None
    coordinates: Coordinates

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

    @classmethod
    def from_orm(cls: Any, venue: Venue):  # type: ignore
        venue.coordinates = {"latitude": venue.latitude, "longitude": venue.longitude}
        return super().from_orm(venue)


class BookingOfferExtraData(BaseModel):
    isbn: str | None


class BookingOfferResponse(BaseModel):
    id: int
    name: str
    extraData: BookingOfferExtraData | None
    image: OfferImageResponse | None
    isDigital: bool
    isPermanent: bool
    subcategoryId: SubcategoryIdEnum
    venue: BookingVenueResponse
    withdrawalDetails: str | None
    withdrawalType: WithdrawalTypeEnum | None
    withdrawalDelay: int | None

    class Config:
        orm_mode = True


class BookingStockResponse(BaseModel):
    id: int
    beginningDatetime: datetime | None
    offer: BookingOfferResponse

    class Config:
        orm_mode = True


class BookingActivationCodeResponse(BaseModel):
    code: str
    expirationDate: datetime | None

    class Config:
        orm_mode = True


class ExternalBookingResponse(BaseModel):
    barcode: str
    seat: str | None

    class Config:
        orm_mode = True


class BookingReponse(BaseModel):
    id: int
    cancellationDate: datetime | None
    cancellationReason: BookingCancellationReasons | None
    confirmationDate: datetime | None
    completedUrl: str | None
    dateUsed: datetime | None
    expirationDate: datetime | None
    qrCodeData: str | None
    quantity: int
    stock: BookingStockResponse
    total_amount: int
    token: str | None
    activationCode: BookingActivationCodeResponse | None
    externalBookings: list[ExternalBookingResponse] | None

    _convert_total_amount = validator("total_amount", pre=True, allow_reuse=True)(convert_to_cent)

    @classmethod
    def from_orm(cls: Any, booking: Booking):  # type: ignore
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
