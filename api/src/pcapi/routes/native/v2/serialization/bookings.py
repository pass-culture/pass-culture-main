import enum
from datetime import datetime
from typing import Any

from pydantic.v1.class_validators import validator
from pydantic.v1.utils import GetterDict

from pcapi.core.bookings import models as bookings_models
from pcapi.core.bookings.api import has_email_been_sent
from pcapi.core.bookings.api import is_external_event_booking_visible
from pcapi.core.bookings.api import is_voucher_displayed
from pcapi.core.categories.subcategories import SEANCE_CINE
from pcapi.core.categories.subcategories import SubcategoryIdEnum
from pcapi.core.geography.models import Address
from pcapi.core.offerers.models import OffererAddress
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.core.offers.models import WithdrawalTypeEnum
from pcapi.core.reactions.models import ReactionTypeEnum
from pcapi.routes.native.v1.serialization.common_models import Coordinates
from pcapi.routes.native.v1.serialization.offers import OfferImageResponse
from pcapi.routes.serialization import ConfiguredBaseModel
from pcapi.routes.shared.price import convert_to_cent


class TicketDisplayEnum(enum.Enum):
    NO_TICKET = "no_ticket"
    EMAIL_SENT = "email_sent"
    EMAIL_WILL_BE_SENT = "email_will_be_sent"
    ONLINE_CODE = "online_code"
    NOT_VISIBLE = "not_visible"
    EVENT_ACCESS = "event_access"
    VOUCHER = "voucher"
    NO_VOUCHER_TICKET = "no_voucher_ticket"


class BookingVenueResponseV2GetterDict(GetterDict):
    def get(self, key: str, default: Any | None = None) -> Any:
        if key == "name":
            return self._obj.common_name

        return super().get(key, default)


class BookingVenueResponseV2(ConfiguredBaseModel):
    id: int
    name: str
    publicName: str | None
    timezone: str
    bannerUrl: str | None
    isOpenToPublic: bool

    class Config:
        getter_dict = BookingVenueResponseV2GetterDict


class BookingOfferExtraDataV2(ConfiguredBaseModel):
    ean: str | None


class BookingOfferResponseAddressV2(ConfiguredBaseModel):
    street: str | None
    postal_code: str
    city: str
    label: str | None
    coordinates: Coordinates
    timezone: str


class BookingOfferResponseV2GetterDict(GetterDict):
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

            return BookingOfferResponseAddressV2(
                street=address.street,
                postal_code=address.postalCode,
                city=address.city,
                label=label,
                coordinates=Coordinates(latitude=address.latitude, longitude=address.longitude),
                timezone=address.timezone,
            )

        return super().get(key, default)


class BookingOfferResponseV2(ConfiguredBaseModel):
    id: int
    address: BookingOfferResponseAddressV2 | None
    booking_contact: str | None
    name: str
    extra_data: BookingOfferExtraDataV2 | None
    image: OfferImageResponse | None
    is_digital: bool
    is_permanent: bool
    subcategory_id: SubcategoryIdEnum
    url: str | None
    venue: BookingVenueResponseV2

    class Config:
        getter_dict = BookingOfferResponseV2GetterDict


class BookingStockResponseV2GetterDict(GetterDict):
    def get(self, key: str, default: Any | None = None) -> Any:
        if key == "priceCategoryLabel":
            price_category = getattr(self._obj, "priceCategory", None)
            return price_category.priceCategoryLabel.label if price_category else None

        return super().get(key, default)


class BookingStockResponseV2(ConfiguredBaseModel):
    id: int
    beginning_datetime: datetime | None
    features: list[str]
    offer: BookingOfferResponseV2
    price: int
    price_category_label: str | None

    _convert_price = validator("price", pre=True, allow_reuse=True)(convert_to_cent)

    class Config:
        getter_dict = BookingStockResponseV2GetterDict


class VoucherResponse(ConfiguredBaseModel):
    data: str | None


class TokenResponse(ConfiguredBaseModel):
    data: str | None


class WithdrawalResponse(ConfiguredBaseModel):
    details: str | None
    type: WithdrawalTypeEnum | None
    delay: int | None


class ActivationCodeResponse(ConfiguredBaseModel):
    code: str
    expiration_date: datetime | None


class ExternalBookingDataResponseV2(ConfiguredBaseModel):
    barcode: str
    seat: str | None


class ExternalBookingResponseV2(ConfiguredBaseModel):
    data: list[ExternalBookingDataResponseV2] | None


class TicketResponse(ConfiguredBaseModel):
    activation_code: ActivationCodeResponse | None
    external_booking: ExternalBookingResponseV2 | None
    display: TicketDisplayEnum
    token: TokenResponse | None
    voucher: VoucherResponse | None
    withdrawal: WithdrawalResponse


class BookingResponseGetterDict(GetterDict):
    def get(self, key: str, default: Any | None = None) -> Any:
        if key == "confirmationDate":
            return self._obj.cancellationLimitDate
        if key == "ticket":
            return self.get_ticket_infos()

        return super().get(key, default)

    def get_ticket_infos(self) -> TicketResponse:
        booking: bookings_models.Booking = self._obj
        stock: Stock = booking.stock
        offer: Offer = stock.offer
        withdrawal = WithdrawalResponse(
            details=offer.withdrawalDetails,
            type=offer.withdrawalType,
            delay=offer.withdrawalDelay,
        )

        if offer.withdrawalType == WithdrawalTypeEnum.NO_TICKET:
            return TicketResponse(
                activation_code=None,
                external_booking=None,
                display=TicketDisplayEnum.NO_TICKET,
                token=None,
                voucher=None,
                withdrawal=withdrawal,
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
                external_booking=ExternalBookingResponseV2(data=booking.externalBookings if booking_visible else None),
                display=TicketDisplayEnum.EVENT_ACCESS if booking_visible else TicketDisplayEnum.NOT_VISIBLE,
                token=None,
                voucher=None,
                withdrawal=withdrawal,
            )

        voucher = (
            VoucherResponse(
                data=getattr(booking, "qrCodeData", None),
            )
            if is_voucher_displayed(offer=offer, isExternal=booking.isExternal)
            else None
        )

        token = TokenResponse(data=booking.token) if not booking.isExternal else None
        display = TicketDisplayEnum.VOUCHER if voucher else TicketDisplayEnum.NO_VOUCHER_TICKET
        if offer.subcategoryId == SEANCE_CINE.id:
            display = TicketDisplayEnum.EVENT_ACCESS

        return TicketResponse(
            activation_code=None,
            external_booking=None,
            display=display,
            token=token,
            voucher=voucher,
            withdrawal=withdrawal,
        )


class BookingResponse(ConfiguredBaseModel):
    id: int
    cancellation_date: datetime | None
    cancellation_reason: bookings_models.BookingCancellationReasons | None
    confirmation_date: datetime | None
    completed_url: str | None
    date_created: datetime
    date_used: datetime | None
    expiration_date: datetime | None
    quantity: int
    stock: BookingStockResponseV2
    total_amount: int
    enable_pop_up_reaction: bool
    can_react: bool
    user_reaction: ReactionTypeEnum | None
    ticket: TicketResponse

    class Config:
        getter_dict = BookingResponseGetterDict


class BookingsResponseV2(ConfiguredBaseModel):
    ended_bookings: list[BookingResponse]
    ongoing_bookings: list[BookingResponse]
    has_bookings_after_18: bool
