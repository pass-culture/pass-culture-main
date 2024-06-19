import datetime
import enum
import typing


if typing.TYPE_CHECKING:
    from pcapi.core.offers.models import Stock


class RedisExternalBookingType(str, enum.Enum):
    CINEMA = "cinema"
    EVENT = "event"


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
ONE_SIDE_BOOKINGS_CANCELLATION_PROVIDERS = {"CDSStocks", "CGRStocks", "EMSStocks"}


def _get_hours_from_timedelta(td: datetime.timedelta) -> float:
    return td.total_seconds() / 3600


BOOKING_CONFIRMATION_ERROR_CLAUSES = {
    "after_creation_delay": f"plus de {_get_hours_from_timedelta(CONFIRM_BOOKING_AFTER_CREATION_DELAY):.0f}h"
    f" après l'avoir réservée et ",
    "before_event_delay": f"moins de {_get_hours_from_timedelta(CONFIRM_BOOKING_BEFORE_EVENT_DELAY):.0f}h"
    f" avant le début de l'évènement",
}

DUO_QUANTITY = 2

BOOKING_EXPORT_HEADERS = (
    "Lieu",
    "Nom de l’offre",
    "Date de l'évènement",
    "EAN",
    "Nom et prénom du bénéficiaire",
    "Email du bénéficiaire",
    "Téléphone du bénéficiaire",
    "Date et heure de réservation",
    "Date et heure de validation",
    "Contremarque",
    "Intitulé du tarif",
    "Prix de la réservation",
    "Statut de la contremarque",
    "Date et heure de remboursement",
    "Type d'offre",
    "Code postal du bénéficiaire",
    "Duo",
)
