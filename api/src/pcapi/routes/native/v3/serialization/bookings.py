import enum
import typing
from datetime import datetime
from typing import Any

from pydantic import model_validator

from pcapi.core.bookings import models as bookings_models
from pcapi.core.bookings import utils as bookings_utils
from pcapi.core.bookings.api import has_email_been_sent
from pcapi.core.bookings.api import is_external_event_booking_visible
from pcapi.core.bookings.api import is_voucher_displayed
from pcapi.core.categories.subcategories import SEANCE_CINE
from pcapi.core.categories.subcategories import SubcategoryIdEnum
from pcapi.core.finance.utils import to_cents
from pcapi.core.offerers.models import Venue
from pcapi.core.offers import constants as offers_constants
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.core.offers.models import WithdrawalTypeEnum
from pcapi.core.reactions.models import ReactionTypeEnum
from pcapi.routes.serialization import HttpBodyModel


class CoordinatesV3(HttpBodyModel):
    latitude: float | None = None
    longitude: float | None = None


class OfferImageV3(HttpBodyModel):
    credit: str | None = None
    url: str


class TicketDisplayEnum(enum.Enum):
    CINEMA_VOUCHER = "cinema_voucher"
    EMAIL_SENT = "email_sent"
    EMAIL_WILL_BE_SENT = "email_will_be_sent"
    EXTERNAL_TICKET = "external_ticket"
    HIDDEN_EXTERNAL_TICKET = "hidden_external_ticket"
    NO_TICKET = "no_ticket"
    ONLINE_CODE = "online_code"
    TICKET = "ticket"
    VOUCHER = "voucher"


class BookingVenueAddressResponseV3(HttpBodyModel):
    id: int | None = None


class BookingVenueResponseV3(HttpBodyModel):
    id: int
    address: BookingVenueAddressResponseV3
    banner_url: str | None = None
    is_open_to_public: bool
    name: str
    public_name: str
    timezone: str

    @model_validator(mode="before")
    @classmethod
    def _pre_process_venue(cls, data: Any) -> Any:
        if isinstance(data, Venue):
            return cls.build(data)
        return data

    @classmethod
    def build(cls, venue: Venue) -> typing.Self:
        return cls(
            id=venue.id,
            address=BookingVenueAddressResponseV3(id=venue.offererAddress.address.id),
            name=venue.publicName,
            public_name=venue.publicName,
            timezone=venue.offererAddress.address.timezone,
            banner_url=venue.bannerUrl,
            is_open_to_public=venue.isOpenToPublic,
        )


class BookingOfferExtraDataV3(HttpBodyModel):
    ean: str | None = None


class BookingOfferResponseAddressV3(HttpBodyModel):
    id: int
    city: str
    coordinates: CoordinatesV3
    label: str | None = None
    postal_code: str
    street: str | None = None
    timezone: str


class BookingOfferResponseV3(HttpBodyModel):
    id: int
    address: BookingOfferResponseAddressV3 | None = None
    booking_contact: str | None = None
    extra_data: BookingOfferExtraDataV3 | None = None
    image: OfferImageV3 | None = None
    is_digital: bool
    is_permanent: bool
    name: str
    subcategory_id: SubcategoryIdEnum
    url: str | None = None
    venue: BookingVenueResponseV3

    @model_validator(mode="before")
    @classmethod
    def _pre_process_offer(cls, data: Any) -> Any:
        if isinstance(data, Offer):
            return cls.build(data)
        return data

    @classmethod
    def build(cls, offer: Offer) -> typing.Self:
        address_response = None
        offerer_address = offer.offererAddress or (offer.venue.offererAddress if offer.venue else None)

        if offerer_address:
            address = offerer_address.address

            address_response = BookingOfferResponseAddressV3(
                id=address.id,
                city=address.city,
                coordinates=CoordinatesV3(latitude=float(address.latitude), longitude=float(address.longitude)),
                label=offerer_address.label,
                postal_code=address.postalCode,
                street=address.street,
                timezone=address.timezone,
            )

        extra_data = None
        if offer.extraData is not None:
            extra_data = BookingOfferExtraDataV3(ean=offer.extraData.get("ean"))

        return cls(
            id=offer.id,
            address=address_response,
            booking_contact=offer.bookingContact,
            extra_data=extra_data,
            image=OfferImageV3(credit=offer.image.credit, url=offer.image.url) if offer.image else None,
            is_digital=offer.isDigital,
            is_permanent=offer.isPermanent,
            name=offer.name,
            subcategory_id=SubcategoryIdEnum(offer.subcategory.id),
            url=offer.url,
            venue=BookingVenueResponseV3.model_validate(offer.venue),
        )


class ScreeningAccessibilityFeatures(HttpBodyModel):
    audio: list[str]
    mental: list[str]
    motor: list[str]
    visual: list[str]

    @classmethod
    def build(cls, features: set[str]) -> typing.Self:
        return cls(
            audio=[f for f in offers_constants.AudioAccessbilityFeatures if f in features],
            mental=[f for f in offers_constants.MentalAccessbilityFeatures if f in features],
            motor=[f for f in offers_constants.MotorAccessbilityFeatures if f in features],
            visual=[f for f in offers_constants.VisualAccessbilityFeatures if f in features],
        )


class ScreeningFeatures(HttpBodyModel):
    accessibility: ScreeningAccessibilityFeatures
    audio: str | None
    language: str | None
    special_event_type: str | None
    video: str | None

    @classmethod
    def build(cls, features: set[str]) -> typing.Self:
        return cls(
            accessibility=ScreeningAccessibilityFeatures.build(features),
            audio=next((f for f in offers_constants.AudioFeatures if f in features), None),
            language=next((f for f in offers_constants.LanguageFeatures if f in features), None),
            special_event_type=next((f for f in offers_constants.SpecialEventFeatures if f in features), None),
            video=next((f for f in offers_constants.VideoFeatures if f in features), None),
        )


class BookingStockResponseV3(HttpBodyModel):
    id: int
    beginning_datetime: datetime | None = None
    is_automatically_used: bool
    offer: BookingOfferResponseV3
    price: int
    price_category_label: str | None = None
    screening_features: ScreeningFeatures

    @model_validator(mode="before")
    @classmethod
    def _pre_process_stock(cls, data: Any) -> Any:
        if isinstance(data, Stock):
            return cls.build(data)
        return data

    @classmethod
    def build(cls, stock: Stock) -> typing.Self:
        return cls(
            id=stock.id,
            is_automatically_used=stock.is_automatically_used,
            beginning_datetime=stock.beginningDatetime,
            screening_features=ScreeningFeatures.build(set(stock.features)),
            offer=BookingOfferResponseV3.build(stock.offer),
            price_category_label=stock.priceCategory.label if stock.priceCategory else None,
            price=to_cents(stock.price),
        )


class VoucherResponse(HttpBodyModel):
    data: str | None = None


class TokenResponse(HttpBodyModel):
    data: str | None = None


class WithdrawalResponse(HttpBodyModel):
    delay: int | None = None
    details: str | None = None
    type: WithdrawalTypeEnum | None = None


class ActivationCodeResponse(HttpBodyModel):
    code: str
    expiration_date: datetime | None = None


class ExternalBookingDataResponseV2(HttpBodyModel):
    barcode: str
    seat: str | None = None


class ExternalBookingResponseV2(HttpBodyModel):
    data: list[ExternalBookingDataResponseV2] | None = None


class TicketResponse(HttpBodyModel):
    activation_code: ActivationCodeResponse | None = None
    display: TicketDisplayEnum
    external_booking: ExternalBookingResponseV2 | None = None
    token: TokenResponse | None = None
    voucher: VoucherResponse | None = None
    withdrawal: WithdrawalResponse | None = None


def get_ticket_infos(booking: bookings_models.Booking) -> TicketResponse:
    stock: Stock = booking.stock
    offer: Offer = stock.offer
    withdrawal = WithdrawalResponse(
        delay=offer.withdrawalDelay,
        details=offer.withdrawalDetails,
        type=offer.withdrawalType,
    )

    if offer.withdrawalType == WithdrawalTypeEnum.NO_TICKET:
        return TicketResponse(
            activation_code=None,
            display=TicketDisplayEnum.NO_TICKET,
            external_booking=None,
            token=None,
            voucher=None,
            withdrawal=withdrawal,
        )

    if offer.withdrawalType == WithdrawalTypeEnum.BY_EMAIL:
        return TicketResponse(
            activation_code=None,
            display=TicketDisplayEnum.EMAIL_SENT
            if has_email_been_sent(stock=stock, withdrawal_delay=offer.withdrawalDelay)
            else TicketDisplayEnum.EMAIL_WILL_BE_SENT,
            external_booking=None,
            token=None,
            voucher=None,
            withdrawal=withdrawal,
        )

    if offer.isDigital:
        return TicketResponse(
            activation_code=ActivationCodeResponse(
                code=booking.activationCode.code, expiration_date=booking.activationCode.expirationDate
            )
            if booking.activationCode
            else None,
            display=TicketDisplayEnum.ONLINE_CODE,
            external_booking=None,
            token=TokenResponse(data=booking.token) if not booking.activationCode else None,
            voucher=None,
            withdrawal=withdrawal,
        )

    if offer.isEvent and booking.isExternal:
        booking_visible = is_external_event_booking_visible(offer=offer, stock=stock)
        return TicketResponse(
            activation_code=None,
            display=TicketDisplayEnum.EXTERNAL_TICKET if booking_visible else TicketDisplayEnum.HIDDEN_EXTERNAL_TICKET,
            external_booking=ExternalBookingResponseV2(
                data=[
                    ExternalBookingDataResponseV2(barcode=ext.barcode, seat=ext.seat)
                    for ext in booking.externalBookings
                ]
                if booking_visible
                else None
            ),
            token=None,
            voucher=None,
            withdrawal=withdrawal,
        )

    voucher = (
        VoucherResponse(data=bookings_utils.get_qr_code_data(booking.token))
        if is_voucher_displayed(offer=offer, isExternal=booking.isExternal)
        else None
    )

    token = TokenResponse(data=booking.token) if not booking.isExternal else None
    display = TicketDisplayEnum.VOUCHER if voucher else TicketDisplayEnum.TICKET
    if offer.subcategoryId == SEANCE_CINE.id:
        display = TicketDisplayEnum.CINEMA_VOUCHER

    return TicketResponse(
        activation_code=None,
        display=display,
        external_booking=None,
        token=token,
        voucher=voucher,
        withdrawal=withdrawal,
    )


class BookingResponseV3(HttpBodyModel):
    id: int
    cancellation_date: datetime | None = None
    cancellation_reason: bookings_models.BookingCancellationReasons | None = None
    can_react: bool
    confirmation_date: datetime | None = None
    completed_url: str | None = None
    date_created: datetime
    date_used: datetime | None = None
    display_as_ended: bool | None = None
    enable_pop_up_reaction: bool
    expiration_date: datetime | None = None
    quantity: int
    stock: BookingStockResponseV3
    ticket: TicketResponse
    total_amount: int
    user_reaction: ReactionTypeEnum | None = None

    @model_validator(mode="before")
    @classmethod
    def _pre_process_booking(cls, data: Any) -> Any:
        if isinstance(data, bookings_models.Booking):
            return cls.build(data)
        return data

    @classmethod
    def build(cls, booking: bookings_models.Booking) -> typing.Self:
        return cls(
            id=booking.id,
            cancellation_date=booking.cancellationDate,
            cancellation_reason=booking.cancellationReason,
            can_react=booking.can_react,
            confirmation_date=booking.cancellationLimitDate,
            completed_url=booking.completedUrl,
            date_created=booking.dateCreated,
            date_used=booking.dateUsed,
            display_as_ended=booking.displayAsEnded,
            enable_pop_up_reaction=booking.enable_pop_up_reaction,
            expiration_date=booking.expirationDate,
            quantity=booking.quantity,
            stock=BookingStockResponseV3.build(booking.stock),
            ticket=get_ticket_infos(booking),
            total_amount=to_cents(booking.total_amount),
            user_reaction=booking.userReaction,
        )
