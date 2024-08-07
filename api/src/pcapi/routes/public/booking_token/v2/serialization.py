from datetime import datetime
from decimal import Decimal
from enum import Enum

import pydantic.v1 as pydantic_v1

from pcapi.core.bookings.models import Booking
from pcapi.core.categories import subcategories_v2
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import format_into_utc_date
from pcapi.utils.human_ids import humanize


class BookingOfferType(str, Enum):
    BIEN = "BIEN"
    EVENEMENT = "EVENEMENT"


class BookingFormula(str, Enum):
    PLACE = "PLACE"
    ABO = "ABO"


class GetBookingResponse(BaseModel):
    bookingId: str
    dateOfBirth: str | None
    datetime: str  # avoid breaking legacy value "" returned for void date
    ean13: str | None
    email: str
    formula: BookingFormula | None = pydantic_v1.Field(
        description="S'applique uniquement aux offres de catégorie Cinéma. Abonnement (ABO) ou place (PLACE)."
    )
    isUsed: bool
    offerId: int
    publicOfferId: str
    offerName: str
    offerType: BookingOfferType
    priceCategoryLabel: str | None
    phoneNumber: str | None
    price: Decimal
    quantity: int
    theater: dict = pydantic_v1.Field(
        description="Identifiant du film et de la salle dans le cas d’une offre synchronisée par Allociné.",
        example={"film_id": "...", "salle_id": "..."},
    )
    userName: str
    firstName: str | None
    lastName: str | None
    venueAddress: str | None
    venueDepartmentCode: str | None
    venueName: str


def get_booking_response(booking: Booking) -> GetBookingResponse:
    if booking.stock.offer.subcategoryId == subcategories_v2.SEANCE_CINE.id:
        formula = BookingFormula.PLACE
    elif booking.stock.offer.subcategoryId in (
        subcategories_v2.CARTE_CINE_ILLIMITE.id,
        subcategories_v2.CARTE_CINE_MULTISEANCES.id,
    ):
        formula = BookingFormula.ABO
    else:
        formula = None

    extra_data = booking.stock.offer.extraData or {}

    birth_date = booking.user.birth_date.isoformat() if booking.user.birth_date else None
    return GetBookingResponse(
        bookingId=humanize(booking.id),  # type: ignore[arg-type]
        dateOfBirth=birth_date,
        datetime=(format_into_utc_date(booking.stock.beginningDatetime) if booking.stock.beginningDatetime else ""),
        ean13=(
            extra_data.get("ean", "") if booking.stock.offer.subcategoryId in subcategories_v2.BOOK_WITH_EAN else None
        ),
        email=booking.email,
        formula=formula,
        isUsed=booking.is_used_or_reimbursed,
        offerId=booking.stock.offer.id,
        publicOfferId=humanize(booking.stock.offer.id),  # type: ignore[arg-type]
        offerName=booking.stock.offer.name,
        offerType=BookingOfferType.EVENEMENT if booking.stock.offer.isEvent else BookingOfferType.EVENEMENT,
        phoneNumber=booking.user.phoneNumber,
        price=booking.amount,
        priceCategoryLabel=booking.priceCategoryLabel,
        quantity=booking.quantity,
        theater=extra_data.get("theater", ""),
        userName=booking.userName,
        firstName=booking.user.firstName,
        lastName=booking.user.lastName,
        venueAddress=booking.venue.street,
        venueDepartmentCode=booking.venue.departementCode,
        venueName=booking.venue.name,
    )


class PostBookingStockModel(BaseModel):
    price: float


class PostBookingBodyModel(BaseModel):
    stock_id: str
    quantity: int

    class Config:
        alias_generator = to_camel


class ActivationCode(BaseModel):
    code: str
    expirationDate: datetime | None
