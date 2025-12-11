import enum

from pcapi.core.bookings.models import Booking
from pcapi.routes.serialization import HttpBodyModel
from pcapi.utils.date import format_into_utc_date
from pcapi.utils.human_ids import humanize


class BookingOfferType(enum.StrEnum):
    BIEN = "BIEN"
    EVENEMENT = "EVENEMENT"


class GetBookingResponse(HttpBodyModel):
    booking_id: str
    date_of_birth: str | None
    datetime: str  # avoid breaking legacy value "" returned for void date
    ean13: str | None
    email: str
    is_used: bool
    offer_id: int
    public_offer_id: str
    offer_name: str
    offer_type: BookingOfferType
    price_category_label: str | None
    phone_number: str | None
    price: float
    quantity: int
    user_name: str
    first_name: str | None
    last_name: str | None
    offer_address: str | None
    offer_department_code: str | None
    venue_name: str


def get_booking_response(booking: Booking) -> GetBookingResponse:
    birth_date = booking.user.birth_date.isoformat() if booking.user.birth_date else None
    return GetBookingResponse(
        booking_id=humanize(booking.id),
        date_of_birth=birth_date,
        datetime=(format_into_utc_date(booking.stock.beginningDatetime) if booking.stock.beginningDatetime else ""),
        ean13=booking.stock.offer.ean,
        email=booking.email,
        is_used=booking.is_used_or_reimbursed,
        offer_id=booking.stock.offer.id,
        public_offer_id=humanize(booking.stock.offer.id),
        offer_name=booking.stock.offer.name,
        offer_type=BookingOfferType.EVENEMENT if booking.stock.offer.isEvent else BookingOfferType.EVENEMENT,
        phone_number=booking.user.phoneNumber,
        price=float(booking.amount),
        price_category_label=booking.priceCategoryLabel,
        quantity=booking.quantity,
        user_name=booking.userName,
        first_name=booking.user.firstName,
        last_name=booking.user.lastName,
        # TODO bdalbianco 02/06/2025: CLEAN_OA remove check when no virtual venue
        offer_address=booking.stock.offer.offererAddress.address.street if booking.stock.offer.offererAddress else None,
        offer_department_code=booking.stock.offer.offererAddress.address.departmentCode
        if booking.stock.offer.offererAddress
        else None,
        venue_name=booking.venue.name,
    )
