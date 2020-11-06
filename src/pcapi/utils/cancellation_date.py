from datetime import datetime
from typing import Optional

from pcapi.core.bookings.api import compute_confirmation_date
from pcapi.utils.date import DATE_ISO_FORMAT
from pcapi.utils.date import format_into_utc_date
from pcapi.utils.date import match_format


def get_cancellation_limit_date(
    beginning_datetime: str, cancellation_limit_date: Optional[str] = None
) -> Optional[str]:
    if not beginning_datetime:
        return None

    if not cancellation_limit_date:
        if match_format(beginning_datetime, DATE_ISO_FORMAT):
            transformed_beginning_datetime = datetime.strptime(beginning_datetime, DATE_ISO_FORMAT)
        else:
            transformed_beginning_datetime = datetime.strptime(beginning_datetime, "%Y-%m-%dT%H:%M:%SZ")

        return format_into_utc_date(compute_confirmation_date(transformed_beginning_datetime, datetime.utcnow()))

    return cancellation_limit_date
