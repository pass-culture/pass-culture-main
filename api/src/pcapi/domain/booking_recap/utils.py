from datetime import datetime

from pcapi.core.bookings.models import BookingStatus


def get_booking_token(
    booking_token: str,
    booking_status: BookingStatus,
    booking_is_educational: bool,
    booking_is_external: bool,
    event_beginning_datetime: datetime | None,
) -> str | None:
    if (
        not event_beginning_datetime
        and booking_status
        not in [
            BookingStatus.REIMBURSED,
            BookingStatus.CANCELLED,
            BookingStatus.USED,
        ]
        or booking_is_educational
        or booking_is_external
    ):
        return None
    return booking_token
