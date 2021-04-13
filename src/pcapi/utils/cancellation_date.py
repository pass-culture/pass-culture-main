from datetime import datetime
from typing import Optional

from pcapi.core.bookings.api import compute_confirmation_date


def get_cancellation_limit_date(
    beginning_datetime: Optional[datetime], cancellation_limit_date: Optional[datetime] = None
) -> Optional[datetime]:
    if not beginning_datetime:
        return None

    if not cancellation_limit_date:
        return compute_confirmation_date(beginning_datetime, datetime.utcnow())

    return cancellation_limit_date
