import datetime


CONFIRM_BOOKING_AFTER_CREATION_DELAY = datetime.timedelta(hours=48)
CONFIRM_BOOKING_BEFORE_EVENT_DELAY = datetime.timedelta(hours=48)
BOOKINGS_AUTO_EXPIRY_DELAY = datetime.timedelta(days=30)
CANCEL_EXPIRED_BOOKINGS_CRON_START_DATE = datetime.datetime(2021, 1, 4)


def _get_hours_from_timedelta(td: datetime.timedelta) -> float:
    return td.total_seconds() / 3600


BOOKING_CONFIRMATION_ERROR_CLAUSES = {
    "after_creation_delay": f"plus de {_get_hours_from_timedelta(CONFIRM_BOOKING_AFTER_CREATION_DELAY):.0f}h"
    f" après l'avoir réservée et ",
    "before_event_delay": f"moins de {_get_hours_from_timedelta(CONFIRM_BOOKING_BEFORE_EVENT_DELAY):.0f}h"
    f" avant le début de l'événement",
}
