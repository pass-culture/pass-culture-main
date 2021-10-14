import datetime
from decimal import Decimal

from dateutil.relativedelta import relativedelta

from pcapi.core.payments.models import DepositType


def _compute_eighteenth_birthday(birth_date: datetime.datetime) -> datetime.datetime:
    return datetime.datetime.combine(birth_date, datetime.time(0, 0)) + relativedelta(years=18)


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
            and offer.subcategory.is_digital_deposit
        )

    def physical_cap_applies(self, offer):
        return (
            not offer.isDigital
            and bool(self.PHYSICAL_CAP)
            and offer.subcategory.is_physical_deposit
        )
    # fmt: on

    def compute_expiration_date(self, birth_date: datetime.datetime) -> datetime.datetime:
        pass


class Grant15LimitConfiguration(BaseLimitConfiguration):
    TOTAL_CAP = Decimal(20)
    DIGITAL_CAP = None
    PHYSICAL_CAP = None

    def compute_expiration_date(self, birth_date: datetime.datetime) -> datetime.datetime:
        return _compute_eighteenth_birthday(birth_date)


class Grant16LimitConfiguration(BaseLimitConfiguration):
    TOTAL_CAP = Decimal(30)
    DIGITAL_CAP = None
    PHYSICAL_CAP = None

    def compute_expiration_date(self, birth_date: datetime.datetime) -> datetime.datetime:
        return _compute_eighteenth_birthday(birth_date)


class Grant17LimitConfiguration(BaseLimitConfiguration):
    TOTAL_CAP = Decimal(30)
    DIGITAL_CAP = None
    PHYSICAL_CAP = None

    def compute_expiration_date(self, birth_date: datetime.datetime) -> datetime.datetime:
        return _compute_eighteenth_birthday(birth_date)


class Grant18LimitConfigurationV1(BaseLimitConfiguration):
    # For now this total cap duplicates what we store in `Deposit.amount`.
    TOTAL_CAP = Decimal(500)
    DIGITAL_CAP = Decimal(200)
    PHYSICAL_CAP = 200

    def compute_expiration_date(self, birth_date: datetime.datetime) -> datetime.datetime:
        return datetime.datetime.utcnow() + relativedelta(years=GRANT_18_VALIDITY_IN_YEARS)


class Grant18LimitConfigurationV2(BaseLimitConfiguration):
    # For now this total cap duplicates what we store in `Deposit.amount`.
    TOTAL_CAP = Decimal(300)
    DIGITAL_CAP = Decimal(100)
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
        return 2
    return 1
