from typing import List
from typing import Tuple

from pcapi.core import mails
from pcapi.core.bookings import constants as booking_constants
from pcapi.core.bookings.models import Booking
from pcapi.core.categories import subcategories
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.users.models import User


def _extract_bookings_information_from_bookings_list(bookings: list[Booking]) -> list[dict]:
    bookings_info = []
    for booking in bookings:
        offer = booking.stock.offer
        bookings_info.append(
            {
                "offer_name": offer.name,
                "venue_name": offer.venue.publicName or offer.venue.name,
            }
        )
    return bookings_info


def _filter_books_bookings(bookings: list[Booking]) -> Tuple[List[Booking], List[Booking]]:
    books_bookings = []
    other_bookings = []

    for booking in bookings:
        if booking.stock.offer.subcategoryId == subcategories.LIVRE_PAPIER.id:
            books_bookings.append(booking)
        else:
            other_bookings.append(booking)

    return books_bookings, other_bookings


def build_soon_to_be_expired_bookings_recap_email_data_for_beneficiary(
    beneficiary: User, bookings: list[Booking], days_before_cancel: int, days_from_booking: int
) -> models.TransactionalEmailData:
    return models.TransactionalEmailData(
        template=TransactionalEmail.BOOKING_SOON_TO_BE_EXPIRED_TO_BENEFICIARY.value,
        params={
            "FIRSTNAME": beneficiary.firstName,
            "BOOKINGS": _extract_bookings_information_from_bookings_list(bookings),
            "DAYS_BEFORE_CANCEL": days_before_cancel,
            "DAYS_FROM_BOOKING": days_from_booking,
        },
    )


def send_soon_to_be_expired_individual_bookings_recap_email_to_beneficiary(
    beneficiary: User, bookings: list[Booking]
) -> bool:
    success = True
    books_bookings, other_bookings = _filter_books_bookings(bookings)
    if books_bookings:
        books_bookings_data = build_soon_to_be_expired_bookings_recap_email_data_for_beneficiary(
            beneficiary=beneficiary,
            bookings=books_bookings,
            days_before_cancel=booking_constants.BOOKS_BOOKINGS_EXPIRY_NOTIFICATION_DELAY.days,
            days_from_booking=booking_constants.BOOKS_BOOKINGS_AUTO_EXPIRY_DELAY.days
            - booking_constants.BOOKS_BOOKINGS_EXPIRY_NOTIFICATION_DELAY.days,
        )
        success &= mails.send(recipients=[beneficiary.email], data=books_bookings_data)

    if other_bookings:
        other_bookings_data = build_soon_to_be_expired_bookings_recap_email_data_for_beneficiary(
            beneficiary=beneficiary,
            bookings=other_bookings,
            days_before_cancel=booking_constants.BOOKINGS_EXPIRY_NOTIFICATION_DELAY.days,
            days_from_booking=booking_constants.BOOKINGS_AUTO_EXPIRY_DELAY.days
            - booking_constants.BOOKINGS_EXPIRY_NOTIFICATION_DELAY.days,
        )
        success &= mails.send(recipients=[beneficiary.email], data=other_bookings_data)

    return success
