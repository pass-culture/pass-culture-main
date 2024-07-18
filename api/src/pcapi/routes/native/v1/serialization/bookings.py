from datetime import datetime
from typing import Any

from pydantic.v1.class_validators import validator

from pcapi.core.bookings import models as bookings_models
from pcapi.core.categories.subcategories_v2 import SubcategoryIdEnum
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import Stock
from pcapi.core.offers.models import WithdrawalTypeEnum
from pcapi.core.reactions.models import ReactionTypeEnum
from pcapi.routes.native.v1.serialization.common_models import Coordinates
from pcapi.routes.native.v1.serialization.offers import OfferImageResponse
from pcapi.routes.serialization import BaseModel
from pcapi.routes.shared.price import convert_to_cent
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import format_into_utc_date
from pydantic import ConfigDict


class BookOfferRequest(BaseModel):
    stock_id: int
    quantity: int
    model_config = ConfigDict(alias_generator=to_camel)


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
    timezone: str
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @classmethod
    def from_orm(cls, venue: Venue) -> "BookingVenueResponse":
        venue.coordinates = {"latitude": venue.latitude, "longitude": venue.longitude}
        venue.address = venue.street
        return super().from_orm(venue)


class BookingOfferExtraData(BaseModel):
    ean: str | None


class BookingOfferResponse(BaseModel):
    id: int
    bookingContact: str | None
    name: str
    extraData: BookingOfferExtraData | None
    image: OfferImageResponse | None
    isDigital: bool
    isPermanent: bool
    subcategoryId: SubcategoryIdEnum
    url: str | None
    venue: BookingVenueResponse
    withdrawalDetails: str | None
    withdrawalType: WithdrawalTypeEnum | None
    withdrawalDelay: int | None
    model_config = ConfigDict(from_attributes=True)


class BookingStockResponse(BaseModel):
    id: int
    beginningDatetime: datetime | None
    features: list[str]
    offer: BookingOfferResponse
    price: int
    priceCategoryLabel: str | None

    _convert_price = validator("price", pre=True, allow_reuse=True)(convert_to_cent)
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_orm(cls, stock: Stock) -> "BookingStockResponse":
        stock_response = super().from_orm(stock)
        price_category = getattr(stock, "priceCategory", None)
        stock_response.priceCategoryLabel = price_category.priceCategoryLabel.label if price_category else None
        return stock_response


class BookingActivationCodeResponse(BaseModel):
    code: str
    expirationDate: datetime | None
    model_config = ConfigDict(from_attributes=True)


class ExternalBookingResponse(BaseModel):
    barcode: str
    seat: str | None
    model_config = ConfigDict(from_attributes=True)


class BookingReponse(BaseModel):
    id: int
    cancellationDate: datetime | None
    cancellationReason: bookings_models.BookingCancellationReasons | None
    confirmationDate: datetime | None
    completedUrl: str | None
    dateCreated: datetime
    dateUsed: datetime | None
    expirationDate: datetime | None
    qrCodeData: str | None
    quantity: int
    stock: BookingStockResponse
    total_amount: int
    token: str | None
    userReaction: ReactionTypeEnum | None
    activationCode: BookingActivationCodeResponse | None
    externalBookings: list[ExternalBookingResponse] | None

    _convert_total_amount = validator("total_amount", pre=True, allow_reuse=True)(convert_to_cent)

    @classmethod
    def from_orm(cls: Any, booking: bookings_models.Booking) -> "BookingReponse":
        booking.confirmationDate = booking.cancellationLimitDate
        serialized = super().from_orm(booking)
        if booking.isExternal:
            serialized.token = None
        return serialized
    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, populate_by_name=True)


class BookingsResponse(BaseModel):
    ended_bookings: list[BookingReponse]
    ongoing_bookings: list[BookingReponse]
    hasBookingsAfter18: bool
    # TODO[pydantic]: The following keys were removed: `json_encoders`.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    model_config = ConfigDict(json_encoders={datetime: format_into_utc_date})


class BookingDisplayStatusRequest(BaseModel):
    ended: bool
