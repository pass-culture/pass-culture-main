import datetime

from pcapi import settings


CONFIRM_BOOKING_AFTER_CREATION_DELAY = datetime.timedelta(hours=48)
CONFIRM_BOOKING_BEFORE_EVENT_DELAY = datetime.timedelta(hours=48)
BOOKINGS_AUTO_EXPIRY_DELAY = datetime.timedelta(days=30)
BOOKS_BOOKINGS_AUTO_EXPIRY_DELAY = datetime.timedelta(days=10)
# TODO(yacine) This date is used to avoid cancellation of bookings created before this date after
#  Should be removed 20 days after activation of the new auto expiry delay
BOOKS_BOOKINGS_AUTO_EXPIRY_DELAY_START_DATE = (
    datetime.datetime.today() - datetime.timedelta(days=11)
    if (settings.IS_TESTING or settings.IS_DEV)
    else datetime.datetime(2021, 10, 1)
)
BOOKINGS_EXPIRY_NOTIFICATION_DELAY = datetime.timedelta(days=7)
BOOKS_BOOKINGS_EXPIRY_NOTIFICATION_DELAY = datetime.timedelta(days=5)
AUTO_USE_AFTER_EVENT_TIME_DELAY = datetime.timedelta(hours=48)


def _get_hours_from_timedelta(td: datetime.timedelta) -> float:
    return td.total_seconds() / 3600


BOOKING_CONFIRMATION_ERROR_CLAUSES = {
    "after_creation_delay": f"plus de {_get_hours_from_timedelta(CONFIRM_BOOKING_AFTER_CREATION_DELAY):.0f}h"
    f" après l'avoir réservée et ",
    "before_event_delay": f"moins de {_get_hours_from_timedelta(CONFIRM_BOOKING_BEFORE_EVENT_DELAY):.0f}h"
    f" avant le début de l'événement",
}
