import pcapi.core.bookings.api as bookings_api
import pcapi.core.bookings.repository as booking_repository


def canceling_token_validation(token: str) -> None:
    booking = booking_repository.find_used_by_token(token)

    if booking:
        bookings_api.mark_as_unused(booking)  # raises error if not allowed
        print(f"The token ({token}) is cancelled")
    else:
        print(f"The token ({token}) is invalid")
