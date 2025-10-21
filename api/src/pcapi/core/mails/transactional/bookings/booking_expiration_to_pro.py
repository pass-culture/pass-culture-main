from pcapi.core import mails
from pcapi.core.bookings import constants as booking_constants
from pcapi.core.bookings.models import Booking
from pcapi.core.categories import subcategories
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.utils import format_price
from pcapi.utils.urls import build_pc_pro_offer_link


def get_bookings_expiration_to_pro_email_data(
    bookings: list[Booking], withdrawal_period: int
) -> models.TransactionalEmailData:
    return models.TransactionalEmailData(
        template=TransactionalEmail.BOOKING_EXPIRATION_TO_PRO.value,
        params={
            "BOOKINGS": _extract_bookings_information_from_bookings_list(bookings),
            "WITHDRAWAL_PERIOD": withdrawal_period,
            "OFFER_ADDRESS": bookings[0].stock.offer.fullAddress,
        },
    )


def _extract_bookings_information_from_bookings_list(bookings: list[Booking]) -> list[dict]:
    bookings_info = []
    for booking in bookings:
        bookings_info.append(
            {
                "offer_name": booking.stock.offer.name,
                "venue_name": booking.stock.offer.venue.common_name,
                "price": str(booking.stock.price) if booking.stock.price > 0 else "gratuit",
                "formatted_price": format_price(booking.stock.price, booking.stock.offer.venue),
                "user_name": booking.userName,
                "user_email": booking.email,
                "pcpro_offer_link": build_pc_pro_offer_link(booking.stock.offer),
            }
        )
    return bookings_info


def send_bookings_expiration_to_pro_email(bookings: list[Booking]) -> None:
    offerer_booking_email = bookings[0].stock.offer.bookingEmail
    if not offerer_booking_email:
        return

    books_bookings, other_bookings = _filter_books_bookings(bookings)
    if books_bookings:
        books_bookings_data = get_bookings_expiration_to_pro_email_data(
            books_bookings, booking_constants.BOOKS_BOOKINGS_AUTO_EXPIRY_DELAY.days
        )
        mails.send(recipients=[offerer_booking_email], data=books_bookings_data)

    if other_bookings:
        other_bookings_data = get_bookings_expiration_to_pro_email_data(
            other_bookings, booking_constants.BOOKINGS_AUTO_EXPIRY_DELAY.days
        )
        mails.send(recipients=[offerer_booking_email], data=other_bookings_data)


def _filter_books_bookings(bookings: list[Booking]) -> tuple[list[Booking], list[Booking]]:
    books_bookings = []
    other_bookings = []

    for booking in bookings:
        if booking.stock.offer.subcategoryId == subcategories.LIVRE_PAPIER.id:
            books_bookings.append(booking)
        else:
            other_bookings.append(booking)

    return books_bookings, other_bookings
