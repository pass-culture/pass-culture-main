from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel

from pcapi.core.categories import subcategories
from pcapi.models import Booking
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import format_into_utc_date
from pcapi.utils.human_ids import humanize


class BookingOfferType(Enum):
    BIEN = "BIEN"
    EVENEMENT = "EVENEMENT"


class BookingFormula(Enum):
    PLACE = "PLACE"
    ABO = "ABO"
    VOID = ""  # avoid breaking legacy value "" returned for void formula


class GetBookingResponse(BaseModel):
    bookingId: str
    dateOfBirth: str  # avoid breaking legacy value "" returned for void date
    datetime: str  # avoid breaking legacy value "" returned for void date
    ean13: Optional[str]
    email: str
    formula: BookingFormula
    isUsed: bool
    offerId: int
    publicOfferId: str
    offerName: str
    offerType: BookingOfferType
    phoneNumber: str
    price: Decimal
    quantity: int
    theater: dict
    userName: str
    venueAddress: Optional[str]
    venueDepartmentCode: Optional[str]
    venueName: str


def get_booking_response(booking: Booking) -> GetBookingResponse:
    if booking.stock.offer.subcategoryId == subcategories.SEANCE_CINE.id:
        formula = BookingFormula.PLACE
    elif booking.stock.offer.subcategoryId in (
        subcategories.CARTE_CINE_ILLIMITE.id,
        subcategories.CARTE_CINE_MULTISEANCES.id,
    ):
        formula = BookingFormula.ABO
    else:
        formula = BookingFormula.VOID

    extra_data = booking.stock.offer.extraData or {}

    return GetBookingResponse(
        bookingId=humanize(booking.id),
        dateOfBirth="",
        datetime=(format_into_utc_date(booking.stock.beginningDatetime) if booking.stock.beginningDatetime else ""),
        ean13=(
            extra_data.get("isbn", "") if booking.stock.offer.subcategoryId in subcategories.BOOK_WITH_ISBN else None
        ),
        email=booking.email,
        formula=formula,
        isUsed=booking.isUsed,
        offerId=booking.stock.offer.id,
        publicOfferId=humanize(booking.stock.offer.id),
        offerName=booking.stock.offer.product.name,
        offerType=BookingOfferType.EVENEMENT if booking.stock.offer.isEvent else BookingOfferType.EVENEMENT,
        phoneNumber="",
        price=booking.amount,
        quantity=booking.quantity,
        theater=extra_data.get("theater", ""),
        userName=booking.publicName,
        venueAddress=booking.venue.address,
        venueDepartmentCode=booking.venue.departementCode,
        venueName=booking.venue.name,
    )


def serialize_booking_minimal(booking: Booking) -> dict:
    serializable_fields = {
        "amount": float(booking.amount),
        "completedUrl": booking.completedUrl,
        "id": humanize(booking.id),
        "isCancelled": booking.isCancelled,
        "quantity": booking.quantity,
        "stockId": humanize(booking.stockId),
        "stock": {"price": booking.stock.price},
        "token": booking.token,
        "activationCode": None,
        "qrCode": booking.qrCode,
    }

    if booking.activationCode:
        serializable_fields["activationCode"] = {
            "code": booking.activationCode.code,
            "expirationDate": booking.activationCode.expirationDate,
        }

    return serializable_fields


class PostBookingStockModel(BaseModel):
    price: float


class PostBookingBodyModel(BaseModel):
    stock_id: str
    quantity: int

    class Config:
        alias_generator = to_camel


class ActivationCode(BaseModel):
    code: str
    expirationDate: Optional[datetime]


class PostBookingResponseModel(BaseModel):
    amount: float
    completedUrl: Optional[str]
    id: str
    isCancelled: bool
    quantity: int
    stock: PostBookingStockModel
    stockId: str
    token: str
    activationCode: Optional[ActivationCode]
    qrCode: Optional[str]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
