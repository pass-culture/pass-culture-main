import datetime
from typing import Optional

from dateutil.relativedelta import relativedelta
import pytz
from sqlalchemy import sql

from pcapi import settings
import pcapi.core.payments.conf as deposit_conf
from pcapi.core.payments.models import CustomReimbursementRule
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
from pcapi.repository import repository

from . import exceptions
from . import repository as payments_repository
from . import validation


def _compute_eighteenth_birthday(birth_date: datetime.datetime) -> datetime.datetime:
    return datetime.datetime.combine(birth_date, datetime.time(0, 0)) + relativedelta(years=18)


def get_granted_deposit(
    beneficiary: User, eligibility: EligibilityType, version: Optional[int] = None
) -> Optional[GrantedDeposit]:
    if eligibility == EligibilityType.UNDERAGE:
        return GrantedDeposit(
            # as the beneficiary activation process may be asynchronous (with Jouve or DMS),
            # beneficiary.age may be > 17 although it was <= 17 when the subscription was made
            amount=deposit_conf.GRANTED_DEPOSIT_AMOUNT_BY_AGE_AND_VERSION[beneficiary.age][1]
            if beneficiary.age in deposit_conf.GRANTED_DEPOSIT_AMOUNT_BY_AGE_AND_VERSION
            else deposit_conf.GRANTED_DEPOSIT_AMOUNT_BY_AGE_AND_VERSION[17][1],
            expiration_date=_compute_eighteenth_birthday(beneficiary.dateOfBirth),
            type=DepositType.GRANT_15_17,
            version=1,
        )

    if eligibility == EligibilityType.AGE18 or settings.IS_INTEGRATION:
        if version is None:
            version = 2
        return GrantedDeposit(
            amount=deposit_conf.GRANTED_DEPOSIT_AMOUNT_BY_AGE_AND_VERSION[ELIGIBILITY_AGE_18][version],
            expiration_date=datetime.datetime.utcnow() + relativedelta(years=deposit_conf.GRANT_18_VALIDITY_IN_YEARS),
            type=DepositType.GRANT_18,
            version=version,
        )

    return None


def create_deposit(
    beneficiary: User,
    deposit_source: str,
    eligibility: Optional[EligibilityType] = EligibilityType.AGE18,
    version: int = None,
) -> Deposit:
    """Create a new deposit for the user if there is no deposit yet.

    The ``version`` argument MUST NOT be used outside (very specific) tests.
    """
    granted_deposit = get_granted_deposit(beneficiary, eligibility, version=version)

    if not granted_deposit:
        raise exceptions.UserNotGrantable()

    if payments_repository.does_deposit_exists_for_beneficiary_and_type(beneficiary, granted_deposit.type):
        raise exceptions.DepositTypeAlreadyGrantedException(granted_deposit.type)

    if beneficiary.has_active_deposit:
        raise exceptions.UserHasAlreadyActiveDeposit()

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


def create_reimbursement_rule(offerer_id, subcategories, rate, start_date, end_date=None):
    rule = CustomReimbursementRule(
        offererId=offerer_id,
        subcategories=subcategories,
        rate=rate,
        timespan=(start_date, end_date),
    )
    validation.validate_reimbursement_rule(rule)
    repository.save(rule)
    return rule


def edit_reimbursement_rule(rule, end_date):
    # To avoid complexity, we do not allow to edit the end date of a
    # rule that already has one.
    if rule.timespan.upper:
        error = "Il n'est pas possible de modifier la date de fin lorsque celle-ci est déjà définie."
        raise exceptions.WrongDateForReimbursementRule(error)
    # `rule.timespan.lower` is a naive datetime but it comes from the
    # database, and is thus UTC. We hence need to localize it so that
    # `_make_timespan()` does not convert it again. This is not needed
    # on production (where the server timezone is UTC), but it's
    # necessary for local development and tests that may be run
    # under a different timezone.
    rule.timespan = rule._make_timespan(pytz.utc.localize(rule.timespan.lower), end_date)
    try:
        validation.validate_reimbursement_rule(rule, check_start_date=False)
    except exceptions.ReimbursementRuleValidationError:
        # Make sure that the change to `timespan` is not accidentally
        # flushed to the database.
        db.session.expire(rule)
        raise
    repository.save(rule)
    return rule
