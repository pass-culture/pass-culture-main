import datetime

import pydantic as pydantic_v2

from pcapi.core.bookings import models as bookings_models
from pcapi.core.categories.subcategories import SubcategoryIdEnum
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.core.offers.models import WithdrawalTypeEnum
from pcapi.core.reactions.models import ReactionTypeEnum
from pcapi.routes.serialization import HttpBodyModel
from pcapi.routes.shared.price import convert_to_cent


class OfferCoordinatesResponse(HttpBodyModel):
    latitude: float | None = None
    longitude: float | None = None


class OfferImageResponse(HttpBodyModel):
    url: str
    credit: str | None = None


class BookOfferRequest(HttpBodyModel):
    stock_id: int
    quantity: int


class BookingDisplayStatusRequest(HttpBodyModel):
    ended: bool


class BookOfferResponse(HttpBodyModel):
    booking_id: int


class BookingVenueResponse(HttpBodyModel):
    id: int
    name: str
    public_name: str
    timezone: str
    banner_url: str | None = None
    is_open_to_public: bool

    @classmethod
    def build(cls, venue: Venue) -> "BookingVenueResponse":
        return cls(
            id=venue.id,
            name=venue.publicName,
            public_name=venue.publicName,
            timezone=venue.offererAddress.address.timezone,
            banner_url=venue.bannerUrl,
            is_open_to_public=venue.isOpenToPublic,
        )


class BookingOfferExtraData(HttpBodyModel):
    ean: str | None = None


class BookingOfferResponseAddress(HttpBodyModel):
    street: str | None = None
    postal_code: str
    city: str
    label: str | None = None
    coordinates: OfferCoordinatesResponse
    timezone: str


class BookingOfferResponse(HttpBodyModel):
    id: int
    address: BookingOfferResponseAddress | None = None
    booking_contact: str | None = None
    name: str
    extra_data: BookingOfferExtraData | None = None
    image: OfferImageResponse | None = None
    is_digital: bool
    is_permanent: bool
    subcategory_id: SubcategoryIdEnum
    url: str | None = None
    venue: BookingVenueResponse
    withdrawal_details: str | None = None
    withdrawal_type: WithdrawalTypeEnum | None = None
    withdrawal_delay: int | None = None

    @classmethod
    def build(cls, offer: Offer) -> "BookingOfferResponse":
        address_response = None
        offerer_address = offer.offererAddress or offer.venue.offererAddress

        if offerer_address:
            addr = offerer_address.address
            address_response = BookingOfferResponseAddress(
                street=addr.street,
                postal_code=addr.postalCode,
                city=addr.city,
                label=offerer_address.label,
                coordinates=OfferCoordinatesResponse(latitude=addr.latitude, longitude=addr.longitude),
                timezone=addr.timezone,
            )

        extra_data = None
        if offer.extraData and offer.extraData.get("ean"):
            extra_data = BookingOfferExtraData(ean=offer.extraData.get("ean"))

        return cls(
            id=offer.id,
            address=address_response,
            booking_contact=offer.bookingContact,
            name=offer.name,
            extra_data=extra_data,
            image=offer.image,
            is_digital=offer.isDigital,
            is_permanent=offer.isPermanent,
            subcategory_id=offer.subcategoryId,
            url=offer.url,
            venue=BookingVenueResponse.build(offer.venue),
            withdrawal_details=offer.withdrawalDetails,
            withdrawal_type=offer.withdrawalType,
            withdrawal_delay=offer.withdrawalDelay,
        )


class BookingStockResponse(HttpBodyModel):
    id: int
    beginning_datetime: datetime.datetime | None = None
    features: list[str]
    offer: BookingOfferResponse
    price: int
    price_category_label: str | None = None

    @classmethod
    def build(cls, stock: Stock) -> "BookingStockResponse":
        price_category = getattr(stock, "priceCategory", None)
        return cls(
            id=stock.id,
            beginning_datetime=stock.beginningDatetime,
            features=stock.features,
            offer=BookingOfferResponse.build(stock.offer),
            price=convert_to_cent(stock.price),
            price_category_label=price_category.priceCategoryLabel.label if price_category else None,
        )


class BookingActivationCodeResponse(HttpBodyModel):
    code: str
    expiration_date: datetime.datetime | None = None


class ExternalBookingResponse(HttpBodyModel):
    barcode: str
    seat: str | None = None


class BookingReponse(HttpBodyModel):
    id: int
    cancellation_date: datetime.datetime | None = None
    cancellation_reason: bookings_models.BookingCancellationReasons | None = None
    confirmation_date: datetime.datetime | None = None
    completed_url: str | None = None
    date_created: datetime.datetime
    date_used: datetime.datetime | None = None
    expiration_date: datetime.datetime | None = None
    qr_code_data: str | None = None
    quantity: int
    stock: BookingStockResponse
    total_amount: int
    token: str | None = None
    enable_pop_up_reaction: bool
    can_react: bool
    user_reaction: ReactionTypeEnum | None = None
    activation_code: BookingActivationCodeResponse | None = None
    external_bookings: list[ExternalBookingResponse] | None = None

    @classmethod
    def build(cls, booking: bookings_models.Booking) -> "BookingReponse":
        token = None if booking.isExternal else booking.token

        return cls(
            id=booking.id,
            cancellation_date=booking.cancellationDate,
            cancellation_reason=booking.cancellationReason,
            confirmation_date=booking.cancellationLimitDate,
            completed_url=booking.completedUrl,
            date_created=booking.dateCreated,
            date_used=booking.dateUsed,
            expiration_date=booking.expirationDate,
            qr_code_data=getattr(booking, "qrCodeData", None),
            quantity=booking.quantity,
            stock=BookingStockResponse.build(booking.stock),
            total_amount=convert_to_cent(booking.total_amount),
            token=token,
            enable_pop_up_reaction=booking.enable_pop_up_reaction,
            can_react=booking.can_react,
            user_reaction=booking.userReaction,
            activation_code=BookingActivationCodeResponse.model_validate(booking.activationCode)
            if booking.activationCode
            else None,
            external_bookings=[ExternalBookingResponse.model_validate(eb) for eb in booking.externalBookings]
            if booking.externalBookings
            else None,
        )


class BookingsResponse(HttpBodyModel):
    ended_bookings: list[BookingReponse]
    ongoing_bookings: list[BookingReponse]
    hasBookingsAfter18: bool

    model_config = pydantic_v2.ConfigDict(
        alias_generator=None,
    )
