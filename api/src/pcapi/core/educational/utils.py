from datetime import datetime


def compute_cancellation_limit_date_for_educational_booking(event_beginning: datetime, booking_creation: datetime):
    return datetime.utcnow()
