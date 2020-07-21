from datetime import datetime, date
from typing import List

from sqlalchemy import Date, cast

from models import BookingSQLEntity, Payment, ApiErrors, PaymentStatus
from models.payment_status import TransactionStatus
from repository import repository

WANTED_SENT_DATE = date.fromisoformat("2020-04-16")
WANTED_BANNED_DATE = date.fromisoformat("2020-04-17")

def cancel_banned_bookings() -> None:
    print("[CANCEL BANNED BOOKINGS] START")
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
            print(f"error : {error.errors} for booking {booking.id}")
            bookings_in_error.append(booking.id)

    print(f"{len(bookings_to_update) - len(bookings_in_error)} BOOKINGS UPDATED")
    print(f"LIST OF UPDATED BOOKINGS")
    print(updated_bookings)

    if len(bookings_in_error) > 0:
        print(f"LIST OF BOOKINGS IN ERROR")
        print(bookings_in_error)

    print("[CANCEL BANNED BOOKINGS] END")


def get_bookings_banned_and_sent() -> List[BookingSQLEntity]:
    reimbursed_bookings_on_wanted_date = BookingSQLEntity.query \
        .join(Payment, Payment.bookingId == BookingSQLEntity.id) \
        .join(PaymentStatus, PaymentStatus.paymentId == Payment.id) \
        .filter(PaymentStatus.status == TransactionStatus.SENT) \
        .filter(cast(PaymentStatus.date, Date) == WANTED_SENT_DATE)

    banned_bookings_on_wanted_date = BookingSQLEntity.query \
        .join(Payment, Payment.bookingId == BookingSQLEntity.id) \
        .join(PaymentStatus, PaymentStatus.paymentId == Payment.id) \
        .filter(PaymentStatus.status == TransactionStatus.BANNED) \
        .filter(cast(PaymentStatus.date, Date) == WANTED_BANNED_DATE)

    currently_banned_bookings = BookingSQLEntity.query \
        .join(Payment, Payment.bookingId == BookingSQLEntity.id) \
        .filter(Payment.currentStatus == TransactionStatus.BANNED)

    return reimbursed_bookings_on_wanted_date \
        .intersect(banned_bookings_on_wanted_date) \
        .intersect(currently_banned_bookings) \
        .all()
