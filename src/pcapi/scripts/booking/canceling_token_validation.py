import pcapi.core.bookings.repository as booking_repository
from pcapi.repository import payment_queries
from pcapi.repository import repository


def canceling_token_validation(token: str) -> None:
    booking = booking_repository.find_used_by_token(token)

    if booking:
        payment = payment_queries.find_by_booking_id(booking_id=booking.id)

        if payment is None:
            booking.isUsed = False
            booking.dateUsed = None
            repository.save(booking)

            print(f"The token ({token}) is cancelled")
        else:
            print(f"We did not cancelled the booking whose token is {token} because it has been already paid")
    else:
        print(f"The token ({token}) is invalid")
