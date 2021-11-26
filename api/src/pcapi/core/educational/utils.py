from datetime import datetime
from datetime import timedelta


def compute_educational_booking_cancellation_limit_date(
    event_beginning: datetime, booking_creation_date: datetime
) -> datetime:
    fifteen_days_before_event = event_beginning - timedelta(days=15)
    return max(fifteen_days_before_event, booking_creation_date)
