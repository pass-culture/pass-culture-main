from typing import List
from typing import Tuple

from pcapi.core.bookings.constants import BOOKS_BOOKINGS_AUTO_EXPIRY_DELAY_START_DATE
from pcapi.core.categories import subcategories
from pcapi.core.users.models import User
from pcapi.models import Booking


def filter_books_bookings(bookings: list[Booking]) -> Tuple[List[Booking], List[Booking]]:

    books_bookings = []
    other_bookings = []

    for booking in bookings:
        if (
            booking.stock.offer.subcategoryId == subcategories.LIVRE_PAPIER.id
            # TODO(yacine) remove this condition below 20 days after activation of FF
            # ENABLE_NEW_AUTO_EXPIRY_DELAY_BOOKS_BOOKINGS
            and booking.dateCreated >= BOOKS_BOOKINGS_AUTO_EXPIRY_DELAY_START_DATE
        ):
            books_bookings.append(booking)
        else:
            other_bookings.append(booking)

    return books_bookings, other_bookings


def build_soon_to_be_expired_bookings_recap_email_data_for_beneficiary(
    beneficiary: User, bookings: list[Booking], days_before_cancel: int, days_from_booking: int
) -> dict:
    return {
        "Mj-TemplateID": 3095065,
        "Mj-TemplateLanguage": True,
        "Vars": {
            "user_firstName": beneficiary.firstName,
            "bookings": _extract_bookings_information_from_bookings_list(bookings),
            "days_before_cancel": days_before_cancel,
            "days_from_booking": days_from_booking,
        },
    }


def _extract_bookings_information_from_bookings_list(bookings: list[Booking]) -> list[dict]:
    bookings_info = []
    for booking in bookings:
        stock = booking.stock
        offer = stock.offer
        bookings_info.append(
            {
                "offer_name": offer.name,
                "venue_name": offer.venue.publicName if offer.venue.publicName else offer.venue.name,
            }
        )
    return bookings_info
