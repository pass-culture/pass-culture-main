import enum
from datetime import datetime
from typing import Any

from pydantic import field_validator
from pydantic import model_validator

from pcapi.core.bookings import models as bookings_models
from pcapi.core.bookings import utils as bookings_utils
from pcapi.core.bookings.api import has_email_been_sent
from pcapi.core.bookings.api import is_external_event_booking_visible
from pcapi.core.bookings.api import is_voucher_displayed
from pcapi.core.categories.subcategories import SEANCE_CINE
from pcapi.core.categories.subcategories import SubcategoryIdEnum
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.core.offers.models import WithdrawalTypeEnum
from pcapi.core.reactions.models import ReactionTypeEnum
from pcapi.routes.serialization import HttpBodyModel
from pcapi.routes.shared.price import convert_to_cent


class CoordinatesV2(HttpBodyModel):
    latitude: float | None = None
    longitude: float | None = None


class OfferImageV2(HttpBodyModel):
    url: str
    credit: str | None = None


class TicketDisplayEnum(enum.Enum):
    EMAIL_SENT = "email_sent"
    EMAIL_WILL_BE_SENT = "email_will_be_sent"
    ONLINE_CODE = "online_code"
    NOT_VISIBLE = "not_visible"
    QR_CODE = "qr_code"
    VOUCHER = "voucher"
    TICKET = "ticket"


class BookingVenueAddressResponseV2(HttpBodyModel):
    id: int | None = None


class BookingVenueResponseV2(HttpBodyModel):
    id: int
    address: BookingVenueAddressResponseV2
    name: str
    public_name: str
    timezone: str
    banner_url: str | None = None
    is_open_to_public: bool

    @model_validator(mode="before")
    @classmethod
    def _pre_process_venue(cls, data: Any) -> Any:
        if isinstance(data, Venue):
            return cls.build(data)
        return data

    @classmethod
    def build(cls, venue: Venue) -> "BookingVenueResponseV2":
        return cls(
            id=venue.id,
            address=BookingVenueAddressResponseV2(id=venue.offererAddress.address.id),
            name=venue.publicName,
            public_name=venue.publicName,
            timezone=venue.offererAddress.address.timezone,
            banner_url=venue.bannerUrl,
            is_open_to_public=venue.isOpenToPublic,
        )


class BookingOfferExtraDataV2(HttpBodyModel):
    ean: str | None = None


class BookingOfferResponseAddressV2(HttpBodyModel):
    id: int
    street: str | None = None
    postal_code: str
    city: str
    label: str | None = None
    coordinates: CoordinatesV2
    timezone: str


class BookingOfferResponseV2(HttpBodyModel):
    id: int
    address: BookingOfferResponseAddressV2 | None = None
    booking_contact: str | None = None
    name: str
    extra_data: BookingOfferExtraDataV2 | None = None
    image: OfferImageV2 | None = None
    is_digital: bool
    is_permanent: bool
    subcategory_id: SubcategoryIdEnum
    url: str | None = None
    venue: BookingVenueResponseV2

    @model_validator(mode="before")
    @classmethod
    def _pre_process_offer(cls, data: Any) -> Any:
        if isinstance(data, Offer):
            return cls.build(data)
        return data

    @classmethod
    def build(cls, offer: Offer) -> "BookingOfferResponseV2":
        address_response = None
        offerer_address = offer.offererAddress or (offer.venue.offererAddress if offer.venue else None)

        if offerer_address:
            addr = offerer_address.address

            address_response = BookingOfferResponseAddressV2(
                id=addr.id,
                street=addr.street,
                postal_code=addr.postalCode,
                city=addr.city,
                label=offerer_address.label,
                coordinates=CoordinatesV2(latitude=addr.latitude, longitude=addr.longitude),
                timezone=addr.timezone,
            )

        extra_data = None
        if offer.extraData is not None:
            extra_data = BookingOfferExtraDataV2(ean=offer.extraData.get("ean"))

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
            venue=BookingVenueResponseV2.model_validate(offer.venue),
        )


class BookingStockResponseV2(HttpBodyModel):
    id: int
    is_automatically_used: bool
    beginning_datetime: datetime | None = None
    features: list[str]
    offer: BookingOfferResponseV2
    price: int
    price_category_label: str | None = None

    @model_validator(mode="before")
    @classmethod
    def _pre_process_stock(cls, data: Any) -> Any:
        if isinstance(data, Stock):
            return cls.build(data)
        return data

    @classmethod
    def build(cls, stock: Stock) -> "BookingStockResponseV2":
        return cls(
            id=stock.id,
            is_automatically_used=stock.is_automatically_used,
            beginning_datetime=stock.beginningDatetime,
            features=stock.features,
            offer=stock.offer,
            price_category_label=stock.priceCategory.priceCategoryLabel.label if stock.priceCategory else None,
            price=convert_to_cent(stock.price),
        )


class VoucherResponse(HttpBodyModel):
    data: str | None = None


class TokenResponse(HttpBodyModel):
    data: str | None = None


class WithdrawalResponse(HttpBodyModel):
    details: str | None = None
    type: WithdrawalTypeEnum | None = None
    delay: int | None = None


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
    external_booking: ExternalBookingResponseV2 | None = None
    display: TicketDisplayEnum
    token: TokenResponse | None = None
    voucher: VoucherResponse | None = None
    withdrawal: WithdrawalResponse | None = None


def get_ticket_infos(booking: bookings_models.Booking) -> TicketResponse:
    stock: Stock = booking.stock
    offer: Offer = stock.offer
    withdrawal = WithdrawalResponse(
        details=offer.withdrawalDetails,
        type=offer.withdrawalType,
        delay=offer.withdrawalDelay,
    )

    if offer.withdrawalType == WithdrawalTypeEnum.BY_EMAIL:
        return TicketResponse(
            activation_code=None,
            external_booking=None,
            display=TicketDisplayEnum.EMAIL_SENT
            if has_email_been_sent(stock=stock, withdrawal_delay=offer.withdrawalDelay)
            else TicketDisplayEnum.EMAIL_WILL_BE_SENT,
            token=None,
            voucher=None,
            withdrawal=withdrawal,
        )

    if offer.isDigital:
        return TicketResponse(
            activation_code=booking.activationCode,
            external_booking=None,
            display=TicketDisplayEnum.ONLINE_CODE,
            token=TokenResponse(data=booking.token) if not booking.activationCode else None,
            voucher=None,
            withdrawal=withdrawal,
        )

    if offer.isEvent and booking.isExternal:
        booking_visible = is_external_event_booking_visible(offer=offer, stock=stock)
        return TicketResponse(
            activation_code=None,
            external_booking=ExternalBookingResponseV2(
                data=[
                    ExternalBookingDataResponseV2(barcode=ext.barcode, seat=ext.seat)
                    for ext in booking.externalBookings
                ]
                if booking_visible
                else None
            ),
            display=TicketDisplayEnum.QR_CODE if booking_visible else TicketDisplayEnum.NOT_VISIBLE,
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
        display = TicketDisplayEnum.QR_CODE

    return TicketResponse(
        activation_code=None,
        external_booking=None,
        display=display,
        token=token,
        voucher=voucher,
        withdrawal=withdrawal,
    )


class BookingResponse(HttpBodyModel):
    id: int
    cancellation_date: datetime | None = None
    cancellation_reason: bookings_models.BookingCancellationReasons | None = None
    confirmation_date: datetime | None = None
    completed_url: str | None = None
    date_created: datetime
    date_used: datetime | None = None
    display_as_ended: bool | None = None
    expiration_date: datetime | None = None
    quantity: int
    stock: BookingStockResponseV2
    total_amount: int
    enable_pop_up_reaction: bool
    can_react: bool
    user_reaction: ReactionTypeEnum | None = None
    ticket: TicketResponse

    @model_validator(mode="before")
    @classmethod
    def _pre_process_booking(cls, data: Any) -> Any:
        if isinstance(data, bookings_models.Booking):
            return cls.build(data)
        return data

    @classmethod
    def build(cls, booking: bookings_models.Booking) -> "BookingResponse":
        return cls(
            id=booking.id,
            cancellation_date=booking.cancellationDate,
            cancellation_reason=booking.cancellationReason,
            confirmation_date=booking.cancellationLimitDate,
            completed_url=booking.completedUrl,
            date_created=booking.dateCreated,
            date_used=booking.dateUsed,
            display_as_ended=booking.displayAsEnded,
            expiration_date=booking.expirationDate,
            quantity=booking.quantity,
            stock=booking.stock,
            total_amount=convert_to_cent(booking.total_amount),
            enable_pop_up_reaction=booking.enable_pop_up_reaction,
            can_react=booking.can_react,
            user_reaction=booking.userReaction,
            ticket=get_ticket_infos(booking),
        )


class BookingsResponseV2(HttpBodyModel):
    ended_bookings: list[BookingResponse]
    ongoing_bookings: list[BookingResponse]
    has_bookings_after_18: bool


class BookingListItemVenueResponse(HttpBodyModel):
    id: int
    name: str
    timezone: str

    @model_validator(mode="before")
    @classmethod
    def _pre_process_venue(cls, data: Any) -> Any:
        if isinstance(data, Venue):
            return cls.build(data)
        return data

    @classmethod
    def build(cls, venue: Venue) -> "BookingListItemVenueResponse":
        return cls(
            id=venue.id,
            name=venue.name,
            timezone=venue.offererAddress.address.timezone,
        )


class BookingListItemOfferResponseTimezone(HttpBodyModel):
    timezone: str
    city: str | None = None
    label: str | None = None


class BookingListItemOfferResponse(HttpBodyModel):
    id: int
    name: str
    image_url: str | None = None
    address: BookingListItemOfferResponseTimezone | None = None
    is_digital: bool
    is_permanent: bool
    withdrawal_delay: int | None = None
    withdrawal_type: WithdrawalTypeEnum | None = None
    subcategory_id: SubcategoryIdEnum
    venue: BookingListItemVenueResponse

    @model_validator(mode="before")
    @classmethod
    def _pre_process_offer(cls, data: Any) -> Any:
        if isinstance(data, Offer):
            return cls.build(data)
        return data

    @classmethod
    def build(cls, offer: Offer) -> "BookingListItemOfferResponse":
        offerer_address = offer.offererAddress or (offer.venue.offererAddress if offer.venue else None)
        address = None
        if offerer_address:
            address = BookingListItemOfferResponseTimezone(
                timezone=offerer_address.address.timezone,
                city=offerer_address.address.city,
                label=offerer_address.label,
            )
        return cls(
            id=offer.id,
            name=offer.name,
            image_url=offer.thumbUrl,
            address=address,
            is_digital=offer.isDigital,
            is_permanent=offer.isPermanent,
            withdrawal_delay=offer.withdrawalDelay,
            withdrawal_type=offer.withdrawalType,
            subcategory_id=offer.subcategoryId,
            venue=BookingListItemVenueResponse.build(offer.venue),
        )


class BookingListItemStockResponse(HttpBodyModel):
    beginning_datetime: datetime | None = None
    is_automatically_used: bool
    offer: BookingListItemOfferResponse


class BookingListItemResponse(HttpBodyModel):
    id: int
    activation_code: ActivationCodeResponse | None = None
    can_react: bool
    cancellation_date: datetime | None = None
    cancellation_reason: bookings_models.BookingCancellationReasons | None = None
    date_created: datetime
    date_used: datetime | None = None
    is_archivable: bool | None = None
    expiration_date: datetime | None = None
    quantity: int
    stock: BookingListItemStockResponse
    total_amount: int
    user_reaction: ReactionTypeEnum | None = None

    @field_validator("total_amount", mode="before")
    @classmethod
    def _convert_total_amount(cls, v: Any) -> Any:
        return convert_to_cent(v)


class BookingsListResponseV2(HttpBodyModel):
    bookings: list[BookingListItemResponse]
