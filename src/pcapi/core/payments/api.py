import datetime
from typing import Optional

from dateutil.relativedelta import relativedelta
from sqlalchemy import sql

from pcapi import settings
import pcapi.core.payments.conf as deposit_conf
from pcapi.core.payments.models import Deposit
from pcapi.core.payments.models import DepositType
from pcapi.core.payments.models import GrantedDeposit
from pcapi.core.users.constants import ELIGIBILITY_AGE_18
from pcapi.core.users.models import EligibilityType
from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.models.payment import Payment
from pcapi.models.payment_status import PaymentStatus
from pcapi.models.payment_status import TransactionStatus

from . import exceptions
from . import repository


def _compute_eighteenth_birthday(birth_date: datetime.datetime) -> datetime.datetime:
    return datetime.datetime.combine(birth_date, datetime.time(0, 0)) + relativedelta(years=18)


def get_granted_deposit(beneficiary: User, version: Optional[int] = None) -> Optional[GrantedDeposit]:
    if beneficiary.eligibility == EligibilityType.UNDERAGE:
        return GrantedDeposit(
            amount=deposit_conf.GRANTED_DEPOSIT_AMOUNT_BY_AGE_AND_VERSION[beneficiary.age][1],
            expiration_date=_compute_eighteenth_birthday(beneficiary.dateOfBirth),
            type=DepositType.GRANT_15_17,
            version=1,
        )

    if beneficiary.eligibility == EligibilityType.AGE18 or settings.IS_INTEGRATION:
        if version is None:
            version = 2
        return GrantedDeposit(
            amount=deposit_conf.GRANTED_DEPOSIT_AMOUNT_BY_AGE_AND_VERSION[ELIGIBILITY_AGE_18][version],
            expiration_date=datetime.datetime.utcnow() + relativedelta(years=deposit_conf.GRANT_18_VALIDITY_IN_YEARS),
            type=DepositType.GRANT_18,
            version=version,
        )

    return None


def create_deposit(beneficiary: User, deposit_source: str, version: int = None) -> Deposit:
    """Create a new deposit for the user if there is no deposit yet.

    The ``version`` argument MUST NOT be used outside (very specific) tests.
    """
    granted_deposit = get_granted_deposit(beneficiary, version)

    if not granted_deposit:
        raise exceptions.UserNotGrantable()

    if repository.does_deposit_exists_for_beneficiary_and_type(beneficiary, granted_deposit.type):
        raise exceptions.DepositTypeAlreadyGrantedException(granted_deposit.type)

    if version is not None:
        granted_deposit.version = version

    deposit = Deposit(
        version=granted_deposit.version,
        type=granted_deposit.type,
        amount=granted_deposit.amount,
        source=deposit_source,
        user=beneficiary,
        expirationDate=granted_deposit.expiration_date,
    )

    return deposit


def bulk_create_payment_statuses(payment_query, status: TransactionStatus, detail=None):
    sel = payment_query.with_entities(Payment.id, sql.literal(status.name), sql.literal(detail))
    query = sql.insert(PaymentStatus).from_select(["paymentId", "status", "detail"], sel)
    db.session.execute(query)
    db.session.commit()
