from typing import List

from models import BookingSQLEntity, Payment
from repository import repository

EXCLUDED_TOKENS = ['2QLYYA', 'BMTUME', 'LUJ9AM', 'DA8YLU', 'Q46YHM']


def correct_booking_status() -> None:
    print("[BOOKINGS UPDATE] START")
    bookings_to_update = get_bookings_cancelled_during_quarantine_with_payment()

    for booking in bookings_to_update:
        booking.isCancelled = False
        booking.isUsed = True
        booking.dateUsed = booking.dateUsed if booking.dateUsed is not None else booking.dateCreated

    repository.save(*bookings_to_update)
    print(f"{len(bookings_to_update)} USERS UPDATED")
    print("[BOOKINGS UPDATE] END")


def get_bookings_cancelled_during_quarantine_with_payment() -> List[BookingSQLEntity]:
    return BookingSQLEntity.query \
        .join(Payment, Payment.bookingId == BookingSQLEntity.id) \
        .filter(Payment.id != None) \
        .filter(BookingSQLEntity.isCancelled == True) \
        .filter(BookingSQLEntity.token.notin_(EXCLUDED_TOKENS)) \
        .all()
