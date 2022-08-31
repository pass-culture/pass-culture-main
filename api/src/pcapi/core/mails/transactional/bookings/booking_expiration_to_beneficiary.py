from typing import List
from typing import Tuple

from pcapi.core import mails
from pcapi.core.bookings import constants as booking_constants
from pcapi.core.bookings.models import Booking
from pcapi.core.categories import subcategories
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.users.models import User


def get_expired_bookings_to_beneficiary_data(
    beneficiary: User, bookings: list[Booking], withdrawal_period: int
) -> models.SendinblueTransactionalEmailData:
    return models.SendinblueTransactionalEmailData(
        template=TransactionalEmail.EXPIRED_BOOKING_TO_BENEFICIARY.value,
        params={
            "FIRSTNAME": beneficiary.firstName,
            "BOOKINGS": _extract_bookings_information_from_bookings_list(bookings),
            "WITHDRAWAL_PERIOD": withdrawal_period,
        },
    )


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


def send_expired_bookings_to_beneficiary_email(beneficiary: User, bookings: list[Booking]) -> None:
    success = True
    books_bookings, other_bookings = _filter_books_bookings(bookings)

    if books_bookings:
        books_bookings_data = get_expired_bookings_to_beneficiary_data(
            beneficiary, books_bookings, booking_constants.BOOKS_BOOKINGS_AUTO_EXPIRY_DELAY.days
        )
        success &= mails.send(recipients=[beneficiary.email], data=books_bookings_data)

    if other_bookings:
        other_bookings_data = get_expired_bookings_to_beneficiary_data(
            beneficiary, other_bookings, booking_constants.BOOKINGS_AUTO_EXPIRY_DELAY.days
        )
        success &= mails.send(recipients=[beneficiary.email], data=other_bookings_data)

    return success  # type: ignore [return-value]


def _filter_books_bookings(bookings: list[Booking]) -> Tuple[List[Booking], List[Booking]]:
    books_bookings = []
    other_bookings = []

    for booking in bookings:
        if booking.stock.offer.subcategoryId == subcategories.LIVRE_PAPIER.id:
            books_bookings.append(booking)
        else:
            other_bookings.append(booking)

    return books_bookings, other_bookings
