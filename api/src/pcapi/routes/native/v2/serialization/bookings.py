from datetime import datetime
from typing import Any

from pydantic.v1.class_validators import validator
from pydantic.v1.utils import GetterDict

from pcapi.core.bookings import models as bookings_models
from pcapi.core.categories.subcategories import HIDEABLE_QRCODE_SUBCATEGORIES
from pcapi.core.categories.subcategories import NO_QRCODE_SUBCATEGORIES
from pcapi.core.categories.subcategories import NUMBER_SECONDS_HIDE_QR_CODE
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
from pcapi.routes.serialization import BaseModel
from pcapi.routes.shared.price import convert_to_cent
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import format_into_utc_date


def get_external_event_visibility(offer: Offer, stock: Stock) -> bool:
    if offer.withdrawalType == WithdrawalTypeEnum.IN_APP:
        if offer.subcategoryId in HIDEABLE_QRCODE_SUBCATEGORIES and stock.beginningDatetime:
            delta = stock.beginningDatetime - datetime.utcnow()
            return delta.total_seconds() < NUMBER_SECONDS_HIDE_QR_CODE
    return True


def get_internal_event_ticket_display(offer: Offer) -> bool:
    if offer.subcategoryId in NO_QRCODE_SUBCATEGORIES:
        return offer.withdrawalType == WithdrawalTypeEnum.ON_SITE
    elif offer.subcategoryId == SEANCE_CINE.id:
        return False

    return True


def determine_email_sent(stock: Stock, withdrawal_delay: int | None) -> bool:
    if withdrawal_delay and stock.beginningDatetime:
        delta = stock.beginningDatetime - datetime.utcnow()
        return delta.total_seconds() < withdrawal_delay
    return False


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

    class Config:
        orm_mode = True
        getter_dict = BookingOfferResponseGetterDict


class BookingStockResponseGetterDict(GetterDict):
    def get(self, key: str, default: Any | None = None) -> Any:
        if key == "priceCategoryLabel":
            price_category = getattr(self._obj, "priceCategory", None)
            return price_category.priceCategoryLabel.label if price_category else None

        return super().get(key, default)


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
        getter_dict = BookingStockResponseGetterDict


class VoucherResponse(BaseModel):
    data: str | None


class EmailResponse(BaseModel):
    sent: bool


class TokenResponse(BaseModel):
    data: str | None
    tokenOnly: bool


class WithdrawalResponse(BaseModel):
    details: str | None
    type: WithdrawalTypeEnum | None
    delay: int | None


class ActivationCodeResponse(BaseModel):
    code: str
    expirationDate: datetime | None

    class Config:
        orm_mode = True


class ExternalBookingDataResponse(BaseModel):
    barcode: str
    seat: str | None

    class Config:
        orm_mode = True


class ExternalBookingResponse(BaseModel):
    isVisible: bool
    data: list[ExternalBookingDataResponse] | None


class TicketResponse(BaseModel):
    voucher: VoucherResponse | None
    email: EmailResponse | None
    token: TokenResponse | None
    withdrawal: WithdrawalResponse
    noTicket: bool
    activationCode: ActivationCodeResponse | None
    externalBooking: ExternalBookingResponse | None


class BookingReponseGetterDict(GetterDict):
    def get(self, key: str, default: Any | None = None) -> Any:
        if key == "confirmationDate":
            return self._obj.cancellationLimitDate
        if key == "ticket":
            return self.get_ticket_infos()

        return super().get(key, default)

    def get_ticket_infos(self) -> TicketResponse:
        stock = self._obj.stock
        offer = stock.offer
        withdrawal = WithdrawalResponse(
            details=offer.withdrawalDetails,
            type=offer.withdrawalType,
            delay=offer.withdrawalDelay,
        )
        no_ticket = offer.withdrawalType == WithdrawalTypeEnum.NO_TICKET
        activation_code = None
        external_booking = None
        token = None
        voucher = None
        token_only = False

        if no_ticket:
            return TicketResponse(
                activationCode=None,
                email=None,
                externalBooking=None,
                noTicket=no_ticket,
                token=None,
                voucher=None,
                withdrawal=withdrawal,
            )

        if offer.withdrawalType == WithdrawalTypeEnum.BY_EMAIL:
            return TicketResponse(
                activationCode=None,
                email=EmailResponse(sent=determine_email_sent(stock, offer.withdrawalDelay)),
                externalBooking=None,
                noTicket=no_ticket,
                token=None,
                voucher=None,
                withdrawal=withdrawal,
            )

        if offer.isDigital:
            no_ticket = False
            activation_code = getattr(self._obj, "activationCode", None)
            return TicketResponse(
                activationCode=activation_code,
                email=None,
                externalBooking=None,
                noTicket=no_ticket,
                token=None,
                voucher=None,
                withdrawal=withdrawal,
            )
        else:
            if offer.isEvent:
                if self._obj.isExternal:
                    is_visible = get_external_event_visibility(offer=offer, stock=stock)
                    external_booking = ExternalBookingResponse(
                        isVisible=is_visible, data=getattr(self._obj, "externalBookings", None) if is_visible else None
                    )
                    return TicketResponse(
                        activationCode=None,
                        email=None,
                        externalBooking=external_booking,
                        noTicket=no_ticket,
                        token=None,
                        voucher=None,
                        withdrawal=withdrawal,
                    )
                else:
                    token_only = get_internal_event_ticket_display(offer=offer)

        voucher = VoucherResponse(
            data=getattr(self._obj, "qrCodeData", None),
        )
        token = TokenResponse(data=None if self._obj.isExternal else self._obj.token, tokenOnly=token_only)

        return TicketResponse(
            activationCode=None,
            email=None,
            externalBooking=None,
            noTicket=no_ticket,
            token=token,
            voucher=voucher,
            withdrawal=withdrawal,
        )


class BookingResponse(BaseModel):
    id: int
    cancellationDate: datetime | None
    cancellationReason: bookings_models.BookingCancellationReasons | None
    confirmationDate: datetime | None
    completedUrl: str | None
    dateCreated: datetime
    dateUsed: datetime | None
    expirationDate: datetime | None
    quantity: int
    stock: BookingStockResponse
    total_amount: int
    enable_pop_up_reaction: bool
    can_react: bool
    userReaction: ReactionTypeEnum | None
    ticket: TicketResponse | None

    class Config:
        orm_mode = True
        alias_generator = to_camel
        allow_population_by_field_name = True
        getter_dict = BookingReponseGetterDict


class BookingsResponse(BaseModel):
    ended_bookings: list[BookingResponse]
    ongoing_bookings: list[BookingResponse]
    hasBookingsAfter18: bool

    class Config:
        json_encoders = {datetime: format_into_utc_date}
