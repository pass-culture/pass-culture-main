import datetime


USE_BOOKING_BEFORE_EVENT_DELAY = datetime.timedelta(hours=72)

CONFIRM_BOOKING_AFTER_CREATION_DELAY = datetime.timedelta(hours=48)
CONFIRM_BOOKING_BEFORE_EVENT_DELAY = datetime.timedelta(hours=72)


def _get_hours_from_timedelta(td: datetime.timedelta) -> float:
    return td.total_seconds()/3600


BOOKING_CONFIRMATION_ERROR_CLAUSES = {
    CONFIRM_BOOKING_AFTER_CREATION_DELAY: f"plus de {_get_hours_from_timedelta(CONFIRM_BOOKING_AFTER_CREATION_DELAY):.0f}h après l'avoir réservée et ",
    CONFIRM_BOOKING_BEFORE_EVENT_DELAY: f"moins de {_get_hours_from_timedelta(CONFIRM_BOOKING_BEFORE_EVENT_DELAY):.0f}h avant le début de l'événement",
}
