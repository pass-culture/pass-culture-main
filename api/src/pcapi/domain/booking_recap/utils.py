from datetime import datetime
from typing import Optional

from pcapi.core.bookings.models import BookingStatus


def get_booking_token(
    booking_token: str,
    booking_status: BookingStatus,
    booking_is_educational: bool,
    event_beginning_datetime: Optional[datetime],
) -> Optional[str]:
    if (
        not event_beginning_datetime
        and booking_status
        not in [
            BookingStatus.REIMBURSED,
            BookingStatus.CANCELLED,
            BookingStatus.USED,
        ]
        or booking_is_educational
    ):
        return None
    return booking_token
