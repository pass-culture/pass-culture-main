from datetime import date
from datetime import datetime
from typing import List

from sqlalchemy import Date
from sqlalchemy import cast

from pcapi.models import ApiErrors
from pcapi.models import Booking
from pcapi.models import Payment
from pcapi.models import PaymentStatus
from pcapi.models.payment_status import TransactionStatus
from pcapi.repository import repository
from pcapi.utils.logger import logger


WANTED_SENT_DATE = date.fromisoformat("2020-04-16")
WANTED_BANNED_DATE = date.fromisoformat("2020-04-17")


def cancel_banned_bookings() -> None:
    logger.info("[CANCEL BANNED BOOKINGS] START")
    bookings_to_update = get_bookings_banned_and_sent()
    bookings_in_error = []
    updated_bookings = []

    for booking in bookings_to_update:
        booking.isCancelled = True
        booking.isUsed = False
        booking.dateUsed = None
        try:
            repository.save(booking)
            updated_bookings.append(booking.id)
        except ApiErrors as error:
            logger.exception(f"{error.errors} for booking {booking.id}")
            bookings_in_error.append(booking.id)

    logger.info(f"{len(updated_bookings)} BOOKINGS UPDATED")
    logger.info(f"LIST OF UPDATED BOOKINGS")
    logger.info(updated_bookings)

    if len(bookings_in_error) > 0:
        logger.error(f"LIST OF BOOKINGS IN ERROR")
        logger.error(bookings_in_error)

    logger.info("[CANCEL BANNED BOOKINGS] END")


def get_bookings_banned_and_sent() -> List[Booking]:
    reimbursed_bookings_on_wanted_date = Booking.query \
        .join(Payment, Payment.bookingId == Booking.id) \
        .join(PaymentStatus, PaymentStatus.paymentId == Payment.id) \
        .filter(PaymentStatus.status == TransactionStatus.SENT) \
        .filter(cast(PaymentStatus.date, Date) == WANTED_SENT_DATE)

    banned_bookings_on_wanted_date = Booking.query \
        .join(Payment, Payment.bookingId == Booking.id) \
        .join(PaymentStatus, PaymentStatus.paymentId == Payment.id) \
        .filter(PaymentStatus.status == TransactionStatus.BANNED) \
        .filter(cast(PaymentStatus.date, Date) == WANTED_BANNED_DATE)

    currently_banned_bookings = Booking.query \
        .join(Payment, Payment.bookingId == Booking.id) \
        .filter(Payment.currentStatus == TransactionStatus.BANNED)

    return reimbursed_bookings_on_wanted_date \
        .intersect(banned_bookings_on_wanted_date) \
        .intersect(currently_banned_bookings) \
        .all()
