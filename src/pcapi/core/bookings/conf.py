import datetime
from decimal import Decimal

from dateutil.relativedelta import relativedelta

from pcapi import settings
from pcapi.models.deposit import DepositType
from pcapi.models.feature import FeatureToggle
from pcapi.models.offer_type import ThingType


CONFIRM_BOOKING_AFTER_CREATION_DELAY = datetime.timedelta(hours=48)
CONFIRM_BOOKING_BEFORE_EVENT_DELAY = datetime.timedelta(hours=48)
BOOKINGS_AUTO_EXPIRY_DELAY = datetime.timedelta(days=30)
BOOKS_BOOKINGS_AUTO_EXPIRY_DELAY = datetime.timedelta(days=10)
# TODO(yacine) This date is used to avoid cancellation of bookings created before this date after
#  Should be removed 20 days after activation of the new auto expiry delay
BOOKS_BOOKINGS_AUTO_EXPIRY_DELAY_START_DATE = (
    datetime.date.today() - datetime.timedelta(days=11)
    if (settings.IS_TESTING or settings.IS_DEV)
    else datetime.date(2021, 9, 22)
)
BOOKINGS_EXPIRY_NOTIFICATION_DELAY = datetime.timedelta(days=7)
BOOKS_BOOKINGS_EXPIRY_NOTIFICATION_DELAY = datetime.timedelta(days=5)
AUTO_USE_AFTER_EVENT_TIME_DELAY = datetime.timedelta(hours=48)


def _get_hours_from_timedelta(td: datetime.timedelta) -> float:
    return td.total_seconds() / 3600


def _compute_next_birthday_date(birth_date: datetime.datetime) -> datetime.datetime:
    if birth_date.replace(year=datetime.date.today().year) > datetime.datetime.now():
        next_birthday = birth_date.replace(year=datetime.date.today().year)
    else:
        next_birthday = birth_date.replace(year=datetime.date.today().year + 1)
    return next_birthday


BOOKING_CONFIRMATION_ERROR_CLAUSES = {
    "after_creation_delay": f"plus de {_get_hours_from_timedelta(CONFIRM_BOOKING_AFTER_CREATION_DELAY):.0f}h"
    f" après l'avoir réservée et ",
    "before_event_delay": f"moins de {_get_hours_from_timedelta(CONFIRM_BOOKING_BEFORE_EVENT_DELAY):.0f}h"
    f" avant le début de l'événement",
}

GRANT_18_VALIDITY_IN_YEARS = 2


class BaseLimitConfiguration:
    TOTAL_CAP = None
    DIGITAL_CAP = None
    DIGITAL_CAPPED_TYPES = {}
    PHYSICAL_CAP = None
    PHYSICAL_CAPPED_TYPES = {}

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

    def compute_expiration_date(self, birth_date: datetime.datetime) -> datetime.datetime:
        pass


class Grant15LimitConfiguration(BaseLimitConfiguration):
    TOTAL_CAP = Decimal(20)
    DIGITAL_CAP = None
    PHYSICAL_CAP = None

    def compute_expiration_date(self, birth_date: datetime.datetime) -> datetime.datetime:
        return _compute_next_birthday_date(birth_date)


class Grant16LimitConfiguration(BaseLimitConfiguration):
    TOTAL_CAP = Decimal(30)
    DIGITAL_CAP = None
    PHYSICAL_CAP = None

    def compute_expiration_date(self, birth_date: datetime.datetime) -> datetime.datetime:
        return _compute_next_birthday_date(birth_date)


class Grant17LimitConfiguration(BaseLimitConfiguration):
    TOTAL_CAP = Decimal(30)
    DIGITAL_CAP = None
    PHYSICAL_CAP = None

    def compute_expiration_date(self, birth_date: datetime.datetime) -> datetime.datetime:
        return _compute_next_birthday_date(birth_date)


class Grant18LimitConfigurationV1(BaseLimitConfiguration):
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

    def compute_expiration_date(self, birth_date: datetime.datetime) -> datetime.datetime:
        return datetime.datetime.utcnow() + relativedelta(years=GRANT_18_VALIDITY_IN_YEARS)


class Grant18LimitConfigurationV2(BaseLimitConfiguration):
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

    def compute_expiration_date(self, birth_date: datetime.datetime) -> datetime.datetime:
        return datetime.datetime.utcnow() + relativedelta(years=GRANT_18_VALIDITY_IN_YEARS)


LIMIT_CONFIGURATIONS = {
    DepositType.GRANT_15: {
        1: Grant15LimitConfiguration(),
    },
    DepositType.GRANT_16: {
        1: Grant16LimitConfiguration(),
    },
    DepositType.GRANT_17: {
        1: Grant17LimitConfiguration(),
    },
    DepositType.GRANT_18: {
        1: Grant18LimitConfigurationV1(),
        2: Grant18LimitConfigurationV2(),
    },
}


def get_current_limit_configuration_for_type(deposit_type: DepositType) -> BaseLimitConfiguration:
    version = get_current_deposit_version_for_type(deposit_type)

    return LIMIT_CONFIGURATIONS[deposit_type][version]


def get_limit_configuration_for_type_and_version(deposit_type: DepositType, version: int) -> BaseLimitConfiguration:
    if version is None:
        version = get_current_deposit_version_for_type(deposit_type)

    return LIMIT_CONFIGURATIONS[deposit_type][version]


def get_current_deposit_version_for_type(deposit_type: DepositType) -> int:
    if deposit_type == DepositType.GRANT_18:
        return 2 if FeatureToggle.APPLY_BOOKING_LIMITS_V2.is_active() else 1
    return 1
