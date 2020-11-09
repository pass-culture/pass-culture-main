from typing import List

from pcapi.models import ApiErrors
from pcapi.models import Booking
from pcapi.models import Payment
from pcapi.repository import repository


EXCLUDED_TOKENS = ['2QLYYA', 'BMTUME', 'LUJ9AM', 'DA8YLU', 'Q46YHM']


def correct_booking_status() -> None:
    print("[BOOKINGS UPDATE] START")
    bookings_to_update = get_bookings_cancelled_during_quarantine_with_payment()
    users_with_not_updated_bookings = []
    users_with_updated_bookings = []

    for booking in bookings_to_update:
        booking.isCancelled = False
        booking.isUsed = True
        booking.dateUsed = booking.dateUsed if booking.dateUsed is not None else booking.dateCreated
        try:
            repository.save(booking)
            users_with_updated_bookings.append(booking.userId)
        except ApiErrors as error:
            print(f"error : {error.errors} for booking {booking.id}")
            users_with_not_updated_bookings.append(booking.userId)

    print(f"{len(bookings_to_update) - len(users_with_not_updated_bookings)} BOOKINGS UPDATED")
    print(f"LIST OF USERS WITH UPDATED BOOKINGS")
    print(users_with_updated_bookings)
    print(f"LIST OF USERS WITH NON UPDATED BOOKINGS")
    print(users_with_not_updated_bookings)
    print("[BOOKINGS UPDATE] END")


def get_bookings_cancelled_during_quarantine_with_payment() -> List[Booking]:
    return Booking.query \
        .join(Payment, Payment.bookingId == Booking.id) \
        .filter(Payment.id != None) \
        .filter(Booking.isCancelled == True) \
        .filter(Booking.token.notin_(EXCLUDED_TOKENS)) \
        .all()
