from datetime import datetime
from datetime import timedelta

from pcapi.core.educational.constants import INSTITUTION_TYPES


def compute_educational_booking_cancellation_limit_date(
    event_beginning: datetime, booking_creation_date: datetime
) -> datetime:
    fifteen_days_before_event = event_beginning - timedelta(days=15)
    return max(fifteen_days_before_event, booking_creation_date)


def get_institution_type_and_name(institution_title: str) -> tuple[str, str]:
    short_type = ""
    for index in INSTITUTION_TYPES:
        if institution_title.strip().startswith(f"{index} "):
            short_type = index
            break

    name = institution_title.replace(index, "", 1).strip()
    long_type = INSTITUTION_TYPES.get(short_type, "").strip()
    return long_type, name
