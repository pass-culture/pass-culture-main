from datetime import datetime
from typing import Any

from pydantic.v1.class_validators import validator
from pydantic.v1.utils import GetterDict

from pcapi.core.bookings import models as bookings_models
from pcapi.core.categories.subcategories import SubcategoryIdEnum
from pcapi.core.geography.models import Address
from pcapi.core.offerers.models import OffererAddress
from pcapi.core.offers.models import Stock
from pcapi.core.offers.models import WithdrawalTypeEnum
from pcapi.core.reactions.models import ReactionTypeEnum
from pcapi.routes.native.v1.serialization.common_models import Coordinates
from pcapi.routes.native.v1.serialization.offers import OfferImageResponse
from pcapi.routes.serialization import BaseModel
from pcapi.routes.shared.price import convert_to_cent
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import format_into_utc_date


class BookOfferRequest(BaseModel):
    stock_id: int
    quantity: int

    class Config:
        alias_generator = to_camel


class BookOfferResponse(BaseModel):
    bookingId: int


class BookingVenueResponseGetterDict(GetterDict):
    def get(self, key: str, default: Any | None = None) -> Any:
        if key == "name":
            return self._obj.common_name

        return super().get(key, default)


class BookingVenueResponse(BaseModel):
    id: int
    name: str
    publicName: str | None
    timezone: str
    bannerUrl: str | None
    isOpenToPublic: bool

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        getter_dict = BookingVenueResponseGetterDict


class BookingOfferExtraData(BaseModel):
    ean: str | None


class BookingOfferResponseAddress(BaseModel):
    street: str | None
    postalCode: str
    city: str
    label: str | None
    coordinates: Coordinates
    timezone: str

    class Config:
        orm_mode = True


class BookingOfferResponseGetterDict(GetterDict):
    def get(self, key: str, default: Any | None = None) -> Any:
        if key == "address":
            offerer_address: OffererAddress | None
            if self._obj.offererAddress:
                offerer_address = self._obj.offererAddress
            else:
                offerer_address = self._obj.venue.offererAddress

            if not offerer_address:
                return None

            address: Address = offerer_address.address
            label = offerer_address.label

            return BookingOfferResponseAddress(
                street=address.street,
                postalCode=address.postalCode,
                city=address.city,
                label=label,
                coordinates=Coordinates(latitude=address.latitude, longitude=address.longitude),
                timezone=address.timezone,
            )

        return super().get(key, default)


class BookingOfferResponse(BaseModel):
    id: int
    address: BookingOfferResponseAddress | None
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

    class Config:
        orm_mode = True
        getter_dict = BookingOfferResponseGetterDict


class BookingStockResponse(BaseModel):
    id: int
    beginningDatetime: datetime | None
    features: list[str]
    offer: BookingOfferResponse
    price: int
    priceCategoryLabel: str | None

    _convert_price = validator("price", pre=True, allow_reuse=True)(convert_to_cent)

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, stock: Stock) -> "BookingStockResponse":
        stock_response = super().from_orm(stock)
        price_category = getattr(stock, "priceCategory", None)
        stock_response.priceCategoryLabel = price_category.priceCategoryLabel.label if price_category else None
        return stock_response


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
    enable_pop_up_reaction: bool
    can_react: bool
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

    class Config:
        orm_mode = True
        alias_generator = to_camel
        allow_population_by_field_name = True


class BookingsResponse(BaseModel):
    ended_bookings: list[BookingReponse]
    ongoing_bookings: list[BookingReponse]
    hasBookingsAfter18: bool

    class Config:
        json_encoders = {datetime: format_into_utc_date}


class BookingDisplayStatusRequest(BaseModel):
    ended: bool
