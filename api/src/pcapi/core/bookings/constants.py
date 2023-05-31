import datetime

from pcapi.core.categories import subcategories


ARCHIVE_DELAY = datetime.timedelta(days=30)
CONFIRM_BOOKING_AFTER_CREATION_DELAY = datetime.timedelta(hours=48)
CONFIRM_BOOKING_BEFORE_EVENT_DELAY = datetime.timedelta(hours=48)
BOOKINGS_AUTO_EXPIRY_DELAY = datetime.timedelta(days=30)
BOOKS_BOOKINGS_AUTO_EXPIRY_DELAY = datetime.timedelta(days=10)
BOOKINGS_EXPIRY_NOTIFICATION_DELAY = datetime.timedelta(days=7)
BOOKS_BOOKINGS_EXPIRY_NOTIFICATION_DELAY = datetime.timedelta(days=5)
AUTO_USE_AFTER_EVENT_TIME_DELAY = datetime.timedelta(hours=48)
REDIS_EXTERNAL_BOOKINGS_NAME = "api:external_bookings:barcodes"
EXTERNAL_BOOKINGS_MINIMUM_ITEM_AGE_IN_QUEUE = 60
FREE_OFFER_SUBCATEGORY_IDS_TO_ARCHIVE = [
    subcategories.ABO_MUSEE.id,
    subcategories.CARTE_MUSEE.id,
    subcategories.ABO_BIBLIOTHEQUE.id,
    subcategories.ABO_MEDIATHEQUE.id,
]


def _get_hours_from_timedelta(td: datetime.timedelta) -> float:
    return td.total_seconds() / 3600


BOOKING_CONFIRMATION_ERROR_CLAUSES = {
    "after_creation_delay": f"plus de {_get_hours_from_timedelta(CONFIRM_BOOKING_AFTER_CREATION_DELAY):.0f}h"
    f" après l'avoir réservée et ",
    "before_event_delay": f"moins de {_get_hours_from_timedelta(CONFIRM_BOOKING_BEFORE_EVENT_DELAY):.0f}h"
    f" avant le début de l'évènement",
}
