from typing import List
from typing import Tuple

from pcapi.core import mails
from pcapi.core.bookings import constants as booking_constants
from pcapi.core.bookings.models import Booking
from pcapi.core.categories import subcategories
from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalEmailData
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers.models import Offerer
from pcapi.domain.postal_code.postal_code import PostalCode
from pcapi.utils.mailing import build_pc_pro_offer_link


def get_bookings_expiration_to_pro_email_data(  # type: ignore [no-untyped-def]
    offerer: Offerer, bookings: list[Booking], withdrawal_period
) -> SendinblueTransactionalEmailData:
    return SendinblueTransactionalEmailData(
        template=TransactionalEmail.BOOKING_EXPIRATION_TO_PRO.value,
        params={
            "BOOKINGS": _extract_bookings_information_from_bookings_list(bookings),
            "DEPARTMENT": PostalCode(offerer.postalCode).get_departement_code(),  # type: ignore [arg-type]
            "WITHDRAWAL_PERIOD": withdrawal_period,
        },
    )


def _extract_bookings_information_from_bookings_list(bookings: list[Booking]) -> list[dict]:
    bookings_info = []
    for booking in bookings:
        bookings_info.append(
            {
                "offer_name": booking.stock.offer.name,
                "venue_name": booking.stock.offer.venue.publicName
                if booking.stock.offer.venue.publicName
                else booking.stock.offer.venue.name,
                "price": str(booking.stock.price) if booking.stock.price > 0 else "gratuit",
                "user_name": booking.userName,
                "user_email": booking.email,
                "pcpro_offer_link": build_pc_pro_offer_link(booking.stock.offer),
            }
        )
    return bookings_info


def send_bookings_expiration_to_pro_email(offerer: Offerer, bookings: list[Booking]) -> bool:
    offerer_booking_email = bookings[0].stock.offer.bookingEmail
    if not offerer_booking_email:
        return True

    success = True
    books_bookings, other_bookings = _filter_books_bookings(bookings)
    if books_bookings:
        books_bookings_data = get_bookings_expiration_to_pro_email_data(
            offerer, books_bookings, booking_constants.BOOKS_BOOKINGS_AUTO_EXPIRY_DELAY.days
        )
        success &= mails.send(recipients=[offerer_booking_email], data=books_bookings_data)

    if other_bookings:
        other_bookings_data = get_bookings_expiration_to_pro_email_data(
            offerer, other_bookings, booking_constants.BOOKINGS_AUTO_EXPIRY_DELAY.days
        )
        success &= mails.send(recipients=[offerer_booking_email], data=other_bookings_data)

    return success


def _filter_books_bookings(bookings: list[Booking]) -> Tuple[List[Booking], List[Booking]]:
    books_bookings = []
    other_bookings = []

    for booking in bookings:
        if booking.stock.offer.subcategoryId == subcategories.LIVRE_PAPIER.id:
            books_bookings.append(booking)
        else:
            other_bookings.append(booking)

    return books_bookings, other_bookings
