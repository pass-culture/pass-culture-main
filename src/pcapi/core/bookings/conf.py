import datetime
from decimal import Decimal

from pcapi import settings
from pcapi.models.feature import FeatureToggle
from pcapi.models.offer_type import ThingType


CONFIRM_BOOKING_AFTER_CREATION_DELAY = datetime.timedelta(hours=48)
CONFIRM_BOOKING_BEFORE_EVENT_DELAY = datetime.timedelta(hours=48)
BOOKINGS_AUTO_EXPIRY_DELAY = datetime.timedelta(days=30)
BOOKS_BOOKINGS_AUTO_EXPIRY_DELAY = datetime.timedelta(days=10)
# TODO(yacine) This date is used to avoid cancellation of bookings created before this date after
#  Should be removed 20 days after activation of the new auto expiry delay
BOOKS_BOOKINGS_AUTO_EXPIRY_DELAY_START_DATE = (
    datetime.date.today() - datetime.timedelta(days=10)
    if (settings.IS_TESTING or settings.IS_DEV)
    else datetime.date(2021, 9, 22)
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


class BaseLimitConfiguration:
    # fmt: off
    def digital_cap_applies(self, offer):
        return (
            offer.isDigital
            and bool(self.DIGITAL_CAP)
            and offer.type in {str(type_) for type_ in self.DIGITAL_CAPPED_TYPES}
        )

    def physical_cap_applies(self, offer):
        return (
            not offer.isDigital
            and bool(self.PHYSICAL_CAP)
            and offer.type in {str(type_) for type_ in self.PHYSICAL_CAPPED_TYPES}
        )
    # fmt: on


class LimitConfigurationV1(BaseLimitConfiguration):
    # For now this total cap duplicates what we store in `Deposit.amount`.
    TOTAL_CAP = Decimal(500)

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

    PHYSICAL_CAP = 200
    PHYSICAL_CAPPED_TYPES = {
        ThingType.AUDIOVISUEL,
        ThingType.INSTRUMENT,
        ThingType.JEUX,
        ThingType.LIVRE_EDITION,
        ThingType.MUSIQUE,
        ThingType.OEUVRE_ART,
        ThingType.MATERIEL_ART_CREA,
    }


class LimitConfigurationV2(BaseLimitConfiguration):
    # For now this total cap duplicates what we store in `Deposit.amount`.
    TOTAL_CAP = Decimal(300)

    DIGITAL_CAP = Decimal(100)
    DIGITAL_CAPPED_TYPES = {
        ThingType.AUDIOVISUEL,
        ThingType.JEUX_VIDEO,
        ThingType.JEUX_VIDEO_ABO,
        ThingType.LIVRE_AUDIO,
        ThingType.LIVRE_EDITION,
        ThingType.MUSIQUE,
        ThingType.PRESSE_ABO,
    }

    PHYSICAL_CAP = None


LIMIT_CONFIGURATIONS = {
    1: LimitConfigurationV1(),
    2: LimitConfigurationV2(),
}


def get_current_deposit_version():
    return 2 if FeatureToggle.APPLY_BOOKING_LIMITS_V2.is_active() else 1
