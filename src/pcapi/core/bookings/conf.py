import datetime
from decimal import Decimal

from pcapi.models.offer_type import ThingType


CONFIRM_BOOKING_AFTER_CREATION_DELAY = datetime.timedelta(hours=48)
CONFIRM_BOOKING_BEFORE_EVENT_DELAY = datetime.timedelta(hours=48)
BOOKINGS_AUTO_EXPIRY_DELAY = datetime.timedelta(days=30)
BOOKINGS_EXPIRY_NOTIFICATION_DELAY = datetime.timedelta(days=7)


def _get_hours_from_timedelta(td: datetime.timedelta) -> float:
    return td.total_seconds() / 3600


BOOKING_CONFIRMATION_ERROR_CLAUSES = {
    "after_creation_delay": f"plus de {_get_hours_from_timedelta(CONFIRM_BOOKING_AFTER_CREATION_DELAY):.0f}h"
    f" après l'avoir réservée et ",
    "before_event_delay": f"moins de {_get_hours_from_timedelta(CONFIRM_BOOKING_BEFORE_EVENT_DELAY):.0f}h"
    f" avant le début de l'événement",
}


class BaseLimitConfiguration:
    def digital_cap_applies(self, offer):
        return offer.isDigital and offer.type in [str(type_) for type_ in self.DIGITAL_CAPPED_TYPES]

    def physical_cap_applies(self, offer):
        return not offer.isDigital and offer.type in [str(type_) for type_ in self.PHYSICAL_CAPPED_TYPES]


class LimitConfigurationV1(BaseLimitConfiguration):
    # For now this total cap duplicates what we store in `Deposit.amount`.
    TOTAL_CAP = 500

    DIGITAL_CAP = Decimal(200)
    DIGITAL_CAPPED_TYPES = {
        ThingType.AUDIOVISUEL,
        ThingType.JEUX_VIDEO,
        ThingType.JEUX_VIDEO_ABO,
        ThingType.LIVRE_AUDIO,
        ThingType.LIVRE_EDITION,
        ThingType.MUSIQUE,
        ThingType.PRESSE_ABO,
    }

    PHYSICAL_CAP = Decimal(200)
    PHYSICAL_CAPPED_TYPES = {
        ThingType.AUDIOVISUEL,
        ThingType.INSTRUMENT,
        ThingType.JEUX,
        ThingType.LIVRE_EDITION,
        ThingType.MUSIQUE,
        ThingType.OEUVRE_ART,
    }


LIMIT_CONFIGURATIONS = {
    1: LimitConfigurationV1(),
}
