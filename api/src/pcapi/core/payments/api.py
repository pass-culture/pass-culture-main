import datetime

from dateutil.relativedelta import relativedelta

from pcapi import settings
import pcapi.core.payments.conf as deposit_conf
from pcapi.core.payments.models import Deposit
from pcapi.core.payments.models import DepositType
from pcapi.core.payments.models import GrantedDeposit
from pcapi.core.users import constants
from pcapi.core.users import models as users_models

from . import exceptions
from . import repository as payments_repository


def _compute_eighteenth_birthday(birth_date: datetime.datetime) -> datetime.datetime:
    return datetime.datetime.combine(birth_date, datetime.time(0, 0)) + relativedelta(years=18)


def get_granted_deposit(
    beneficiary: users_models.User,
    eligibility: users_models.EligibilityType,
    age_at_registration: int | None = None,
) -> GrantedDeposit | None:
    if eligibility == users_models.EligibilityType.UNDERAGE:
        if age_at_registration not in constants.ELIGIBILITY_UNDERAGE_RANGE:
            raise exceptions.UserNotGrantable("User is not eligible for underage deposit")

        return GrantedDeposit(
            amount=deposit_conf.GRANTED_DEPOSIT_AMOUNTS_FOR_UNDERAGE_BY_AGE[age_at_registration],
            expiration_date=_compute_eighteenth_birthday(beneficiary.dateOfBirth),  # type: ignore [arg-type]
            type=DepositType.GRANT_15_17,
            version=1,
        )

    if eligibility == users_models.EligibilityType.AGE18 or settings.IS_INTEGRATION:
        return GrantedDeposit(
            amount=deposit_conf.GRANTED_DEPOSIT_AMOUNTS_FOR_18_BY_VERSION[2],
            expiration_date=datetime.datetime.utcnow() + relativedelta(years=deposit_conf.GRANT_18_VALIDITY_IN_YEARS),
            type=DepositType.GRANT_18,
            version=2,
        )

    return None


def create_deposit(
    beneficiary: users_models.User,
    deposit_source: str,
    eligibility: users_models.EligibilityType,
    age_at_registration: int | None = None,
) -> Deposit:
    """Create a new deposit for the user if there is no deposit yet."""
    granted_deposit = get_granted_deposit(
        beneficiary,
        eligibility,
        age_at_registration=age_at_registration,
    )

    if not granted_deposit:
        raise exceptions.UserNotGrantable()

    if payments_repository.does_deposit_exists_for_beneficiary_and_type(beneficiary, granted_deposit.type):
        raise exceptions.DepositTypeAlreadyGrantedException(granted_deposit.type)

    if beneficiary.has_active_deposit:
        raise exceptions.UserHasAlreadyActiveDeposit()

    deposit = Deposit(
        version=granted_deposit.version,
        type=granted_deposit.type,
        amount=granted_deposit.amount,
        source=deposit_source,
        user=beneficiary,
        expirationDate=granted_deposit.expiration_date,
    )

    return deposit
