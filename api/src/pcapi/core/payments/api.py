import datetime

from dateutil.relativedelta import relativedelta
import pytz

from pcapi import settings
import pcapi.core.payments.conf as deposit_conf
from pcapi.core.payments.models import CustomReimbursementRule
from pcapi.core.payments.models import Deposit
from pcapi.core.payments.models import DepositType
from pcapi.core.payments.models import GrantedDeposit
from pcapi.core.users import constants
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.repository import repository
import pcapi.utils.db as db_utils

from . import exceptions
from . import repository as payments_repository
from . import validation


def _compute_eighteenth_birthday(birth_date: datetime.datetime) -> datetime.datetime:
    return datetime.datetime.combine(birth_date, datetime.time(0, 0)) + relativedelta(years=18)


def get_granted_deposit(
    beneficiary: users_models.User,
    eligibility: users_models.EligibilityType,
    age_at_registration: int | None = None,
    version: int | None = None,
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
        if version is None:
            version = 2
        return GrantedDeposit(
            amount=deposit_conf.GRANTED_DEPOSIT_AMOUNTS_FOR_18_BY_VERSION[version],
            expiration_date=datetime.datetime.utcnow() + relativedelta(years=deposit_conf.GRANT_18_VALIDITY_IN_YEARS),
            type=DepositType.GRANT_18,
            version=version,
        )

    return None


def create_deposit(
    beneficiary: users_models.User,
    deposit_source: str,
    eligibility: users_models.EligibilityType,
    version: int | None = None,
    age_at_registration: int | None = None,
) -> Deposit:
    """Create a new deposit for the user if there is no deposit yet.

    The ``version`` argument MUST NOT be used outside (very specific) tests.
    """
    granted_deposit = get_granted_deposit(
        beneficiary,
        eligibility,
        age_at_registration=age_at_registration,
        version=version,
    )

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


def create_offerer_reimbursement_rule(offerer_id, subcategories, rate, start_date, end_date=None):  # type: ignore [no-untyped-def]
    return _create_reimbursement_rule(
        offerer_id=offerer_id,
        subcategories=subcategories,
        rate=rate,
        start_date=start_date,
        end_date=end_date,
    )


def create_offer_reimbursement_rule(offer_id, amount, start_date, end_date=None):  # type: ignore [no-untyped-def]
    return _create_reimbursement_rule(
        offer_id=offer_id,
        amount=amount,
        start_date=start_date,
        end_date=end_date,
    )


def _create_reimbursement_rule(  # type: ignore [no-untyped-def]
    offerer_id=None, offer_id=None, subcategories=None, rate=None, amount=None, start_date=None, end_date=None
):
    subcategories = subcategories or []
    if not (bool(offerer_id) ^ bool(offer_id)):
        raise ValueError("Must provider offer or offerer (but not both)")
    if not (bool(rate) ^ bool(amount)):
        raise ValueError("Must provider rate or amount (but not both)")
    if not (bool(rate) or not bool(offerer_id)):
        raise ValueError("Rate must be specified only with an offerere (not with an offer)")
    if not (bool(amount) or not bool(offer_id)):
        raise ValueError("Amount must be specified only with an offer (not with an offerer)")
    if not start_date:
        raise ValueError("Start date must be provided")
    rule = CustomReimbursementRule(
        offererId=offerer_id,
        offerId=offer_id,
        subcategories=subcategories,
        rate=rate,  # only for offerers
        amount=amount,  # only for offers
        timespan=(start_date, end_date),
    )
    validation.validate_reimbursement_rule(rule)
    repository.save(rule)
    return rule


def edit_reimbursement_rule(rule, end_date):  # type: ignore [no-untyped-def]
    # To avoid complexity, we do not allow to edit the end date of a
    # rule that already has one.
    if rule.timespan.upper:
        error = "Il n'est pas possible de modifier la date de fin lorsque celle-ci est déjà définie."
        raise exceptions.WrongDateForReimbursementRule(error)
    # `rule.timespan.lower` is a naive datetime but it comes from the
    # database, and is thus UTC. We hence need to localize it so that
    # `make_timerange()` does not convert it again. This is not needed
    # on production (where the server timezone is UTC), but it's
    # necessary for local development and tests that may be run
    # under a different timezone.
    rule.timespan = db_utils.make_timerange(pytz.utc.localize(rule.timespan.lower), end_date)
    try:
        validation.validate_reimbursement_rule(rule, check_start_date=False)
    except exceptions.ReimbursementRuleValidationError:
        # Make sure that the change to `timespan` is not accidentally
        # flushed to the database.
        db.session.expire(rule)
        raise
    repository.save(rule)
    return rule
