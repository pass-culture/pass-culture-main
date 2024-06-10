from pcapi.core.bookings.models import Booking
from pcapi.utils.date import format_time_in_second_to_human_readable


def get_booking_token(booking: Booking) -> str:
    return booking.activationCode.code if booking.activationCode else booking.token


def get_offer_withdrawal_delay(booking: Booking) -> str | None:
    return (
        format_time_in_second_to_human_readable(booking.stock.offer.withdrawalDelay)
        if booking.stock.offer.withdrawalDelay
        else None
    )


def get_offer_withdrawal_details(booking: Booking) -> str | None:
    return booking.stock.offer.withdrawalDetails or None


def get_offer_withdrawal_type(booking: Booking) -> str:
    return booking.stock.offer.withdrawalType


def get_offerer_name(booking: Booking) -> str:
    return booking.stock.offer.venue.managingOfferer.name


def get_venue_street(booking: Booking) -> str:
    return booking.stock.offer.street
