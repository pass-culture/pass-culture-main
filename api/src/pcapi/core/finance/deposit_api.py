import datetime
import decimal
import logging
import typing

from dateutil.relativedelta import relativedelta
import sqlalchemy.orm as sa_orm

from pcapi import settings
import pcapi.core.bookings.models as bookings_models
from pcapi.core.categories.models import ReimbursementRuleChoices
from pcapi.core.external import batch as push_notifications
import pcapi.core.external.attributes.api as external_attributes_api
import pcapi.core.mails.transactional as transactional_mails
from pcapi.core.users import utils as users_utils
import pcapi.core.users.constants as users_constants
import pcapi.core.users.models as users_models
from pcapi.models import db
from pcapi.models import feature
from pcapi.repository import transaction

from . import conf
from . import exceptions
from . import models
from . import repository
from . import utils


logger = logging.getLogger(__name__)

RECREDIT_UNDERAGE_USERS_BATCH_SIZE = 500


def compute_deposit_expiration_date(
    beneficiary: users_models.User, deposit_type: models.DepositType
) -> datetime.datetime:
    if deposit_type == models.DepositType.GRANT_15_17:
        return compute_underage_deposit_expiration_datetime(beneficiary.birth_date)

    if feature.FeatureToggle.WIP_ENABLE_CREDIT_V3.is_active():
        return compute_deposit_expiration_date_v3(beneficiary)

    expiration_date = datetime.datetime.utcnow().date() + relativedelta(years=conf.GRANT_18_VALIDITY_IN_YEARS)
    expiration_datetime = datetime.datetime.combine(expiration_date, datetime.time.max)
    return expiration_datetime


def compute_deposit_expiration_date_v3(beneficiary: users_models.User) -> datetime.datetime:
    if not beneficiary.birth_date:
        raise ValueError(f"Beneficiary {beneficiary.id} has no birth date")

    # We add here an 11h buffer for the french territories overseas.
    # TODO: use the actual department code of the user
    return beneficiary.birth_date + relativedelta(years=21, hours=11)


def compute_underage_deposit_expiration_datetime(birth_date: datetime.date | None) -> datetime.datetime:
    if not birth_date:
        raise exceptions.UserNotGrantable("User has no validated birth date")
    return datetime.datetime.combine(birth_date, datetime.time(0, 0)) + relativedelta(years=18)


def get_granted_deposit(
    beneficiary: users_models.User,
    eligibility: users_models.EligibilityType,
    age_at_registration: int | None = None,
) -> models.GrantedDeposit | None:
    if eligibility == users_models.EligibilityType.UNDERAGE:
        if age_at_registration not in users_constants.ELIGIBILITY_UNDERAGE_RANGE:
            raise exceptions.UserNotGrantable("User is not eligible for underage deposit")

        return models.GrantedDeposit(
            amount=conf.GRANTED_DEPOSIT_AMOUNTS_FOR_UNDERAGE_BY_AGE[age_at_registration],
            expiration_date=compute_deposit_expiration_date(beneficiary, deposit_type=models.DepositType.GRANT_15_17),
            type=models.DepositType.GRANT_15_17,
            version=1,
        )

    if eligibility == users_models.EligibilityType.AGE18:
        return models.GrantedDeposit(
            amount=conf.GRANTED_DEPOSIT_AMOUNT_18_v2,
            expiration_date=compute_deposit_expiration_date(beneficiary, deposit_type=models.DepositType.GRANT_18),
            type=models.DepositType.GRANT_18,
            version=2,
        )

    return None


def _recredit_user(user: users_models.User) -> models.Recredit | None:
    if (
        feature.FeatureToggle.WIP_ENABLE_CREDIT_V3.is_active()
        and datetime.datetime.utcnow() > settings.CREDIT_V3_DECREE_DATETIME
    ):
        return _recredit_user_v3(user)
    return _recredit_user_v2(user)


def _recredit_user_v3(user: users_models.User) -> models.Recredit | None:

    if not user.deposit or not user.age:
        return None
    if not (user_eligibility := user.eligibility):
        return None

    if user.deposit.type == models.DepositType.GRANT_17_18:
        return _recredit_grant_17_18_deposit_using_age(user)

    new_deposit = _create_new_deposit_and_transfer_funds(user, user_eligibility)
    latest_age_related_recredit = next(
        (
            recredit
            for recredit in new_deposit.recredits
            if recredit.recreditType != models.RecreditType.PREVIOUS_DEPOSIT
        ),
        None,
    )

    return latest_age_related_recredit


def _create_new_deposit_and_transfer_funds(
    user: users_models.User, user_eligibility: users_models.EligibilityType
) -> models.Deposit:
    from pcapi.core.users.api import get_domains_credit

    if not user.deposit or not user.age:
        raise ValueError("User must have a deposit and age. This function should not be called.")

    # Extract what needs to be transfered from current active deposit
    domains_credit = get_domains_credit(user)
    if not domains_credit:
        amount_to_transfer = decimal.Decimal(0)
    else:
        amount_to_transfer = decimal.Decimal(domains_credit.all.remaining)
    booking_that_can_be_cancelled = [
        booking
        for booking in user.deposit.bookings
        if booking.status in [bookings_models.BookingStatus.CONFIRMED, bookings_models.BookingStatus.USED]
        # Ignore non-reimbursed bookings. Thay are not cancelled by the user nor the cultural partners.
        and not booking.stock.offer.subcategory.reimbursement_rule == ReimbursementRuleChoices.NOT_REIMBURSED
    ]

    # create new deposit
    expire_current_deposit_for_user(user)
    new_deposit = create_deposit_v3(
        user,
        deposit_source="Transfer deposit to age_17_18 type",
        eligibility=user_eligibility,
    )

    # Transfer bookings and update deposit amount
    for booking in booking_that_can_be_cancelled:
        amount_to_transfer += booking.total_amount
        booking.depositId = new_deposit.id

    if amount_to_transfer:
        _recredit_deposit(
            new_deposit, user.age, recredit_type=models.RecreditType.PREVIOUS_DEPOSIT, amount=amount_to_transfer
        )
    return new_deposit


def _recredit_user_v2(user: users_models.User) -> models.Recredit | None:
    """
    Recredits the user of all their missing recredits.
    :return: The most recent recredit.
    """
    deposit = user.deposit
    if deposit is None or user.age is None:
        return None

    min_age_between_deposit_and_now = _get_known_age_at_deposit(user)
    if min_age_between_deposit_and_now is None or user.age < min_age_between_deposit_and_now:
        # this can happen when the beneficiary activates their credit at 17, and their age is
        # set back to 15 years old, either through manual backoffice action or automatic identity
        # provider check
        min_age_between_deposit_and_now = user.age

    latest_recredit: models.Recredit | None = None
    for age in range(min_age_between_deposit_and_now, user.age + 1):
        if not _can_be_recredited(user, age):
            continue
        latest_recredit = _recredit_deposit(deposit, age, recredit_type=conf.RECREDIT_TYPE_AGE_MAPPING[age])

    return latest_recredit


def _recredit_grant_17_18_deposit_using_age(user: users_models.User) -> models.Recredit | None:
    from pcapi.core.users import eligibility_api

    current_age = user.age
    if not current_age or not user.deposit:
        return None

    age_at_first_registration = eligibility_api.get_age_at_first_registration(
        user, users_models.EligibilityType.AGE17_18
    )
    latest_age_related_recredit: models.Recredit | None = None
    starting_age, end_age = sorted([age_at_first_registration or current_age, current_age])
    for age_to_recredit in range(starting_age, end_age + 1):
        recredit_type_to_create = conf.RECREDIT_TYPE_AGE_MAPPING.get(age_to_recredit)
        if not recredit_type_to_create:
            continue

        recredit_amount = conf.get_credit_amount_per_age(age_to_recredit)
        if not recredit_amount:
            continue

        has_been_recredited = any(
            recredit.recreditType == recredit_type_to_create for recredit in user.deposit.recredits
        )
        if has_been_recredited:
            continue

        latest_age_related_recredit = _recredit_deposit(user.deposit, age_to_recredit, recredit_type_to_create)

    return latest_age_related_recredit


def _recredit_deposit(
    deposit: models.Deposit, age: int, recredit_type: models.RecreditType, amount: decimal.Decimal | None = None
) -> models.Recredit:
    if amount is None:
        amount = conf.get_credit_amount_per_age(age)
    if amount is None:
        raise ValueError(f"Could not create recredit with unknown amount. Deposit: {deposit.id}, user {deposit.userId}")
    recredit = models.Recredit(
        deposit=deposit,
        amount=amount,
        recreditType=recredit_type,
    )
    deposit.amount += recredit.amount

    db.session.add(recredit)
    db.session.flush()

    return recredit


def recredit_new_deposit_after_validation_of_incident_on_expired_deposit(
    booking_incident: models.BookingFinanceIncident,
) -> models.Recredit | None:
    """
    During the transition from v2 deposits to v3 deposits, some 15-17 deposits will be prematurely expired
    and a new 17-18 will start, cumulating the remaining deposit amount.
    To adapt this cumulation to incidents concerning a booking made with a 15-17 expired deposit,
    we add the incident amount on the 17-18 deposit, via a specific Recredit object.
    """
    if booking := booking_incident.booking:
        # helps mypy
        if booking.deposit is None:  # in the case of a finance incident, the deposit is never None
            return None
        if booking.deposit.expirationDate is None:  # expirationDate is never None
            return None
        if booking.user.deposit is None:  # can't be None if booking.deposit isn't
            return None

        if (
            booking.deposit.expirationDate < datetime.datetime.utcnow()
            and booking.deposit != booking.user.deposit
            and booking.user.deposit.type == models.DepositType.GRANT_17_18
        ):
            recredit = models.Recredit(
                deposit=booking.user.deposit,
                amount=utils.cents_to_full_unit(booking_incident.due_amount_by_offerer),
                recreditType=models.RecreditType.FINANCE_INCIDENT_RECREDIT,
                comment="Suite à la validation d'un incident finance, recrédit du crédit 17-18 après l'expiration prématurée du crédit 15-17 due à la transition vers la v3",
            )
            booking.user.deposit.amount += recredit.amount
            db.session.add(recredit)
            return recredit
    return None


def upsert_deposit(
    user: users_models.User,
    deposit_source: str,
    eligibility: users_models.EligibilityType,
    age_at_registration: int | None = None,
) -> models.Deposit:
    """
    Create a deposit for the user. If the deposit already exists, try to recredit the user instead.
    """
    if eligibility == users_models.EligibilityType.AGE18:
        has_active_underage_deposit = (
            user.deposit
            and user.deposit.type == models.DepositType.GRANT_15_17
            and (user.deposit.expirationDate is None or user.deposit.expirationDate >= datetime.datetime.utcnow())
        )
        if has_active_underage_deposit:
            expire_current_deposit_for_user(user)

    # If the user has an underage deposit, and is eligibile for a 17-18 deposit, they sometimes will have an expired underage deposit. (This should not usually be the case.)
    # To compensate, we extend the expiration date of the underage deposit to the future.
    # The deposit will be expired by the following code anyway (cf. _recredit_user).
    if (
        eligibility == users_models.EligibilityType.AGE17_18
        and user.deposit
        and user.deposit.type == models.DepositType.GRANT_15_17
        and not user.has_active_deposit
    ):
        user.deposit.expirationDate = datetime.datetime.utcnow() + relativedelta(hours=1)

    if not user.has_active_deposit:
        deposit = create_deposit(user, deposit_source, eligibility, age_at_registration)
        user.recreditAmountToShow = deposit.amount
        return deposit

    if not user.deposit:
        raise ValueError(f"failed to create deposit for {user = }")

    recredit = _recredit_user(user)
    if not recredit:
        raise exceptions.UserCannotBeRecredited()
    user.recreditAmountToShow = recredit.amount

    return user.deposit


def create_deposit(
    beneficiary: users_models.User,
    deposit_source: str,
    eligibility: users_models.EligibilityType,
    age_at_registration: int | None = None,
) -> models.Deposit:
    """Create a new deposit for the user if there is no deposit yet."""
    if feature.FeatureToggle.WIP_ENABLE_CREDIT_V3.is_active():
        return create_deposit_v3(beneficiary, deposit_source, eligibility)

    return create_deposit_v2(beneficiary, deposit_source, eligibility)


def create_deposit_v3(
    beneficiary: users_models.User,
    deposit_source: str,
    eligibility: users_models.EligibilityType,
) -> models.Deposit:
    if eligibility in [users_models.EligibilityType.UNDERAGE, users_models.EligibilityType.AGE18]:
        return create_deposit_v2(beneficiary, deposit_source, eligibility)

    if repository.deposit_exists_for_beneficiary_and_type(beneficiary, models.DepositType.GRANT_17_18):
        raise exceptions.DepositTypeAlreadyGrantedException(models.DepositType.GRANT_17_18)

    if beneficiary.has_active_deposit:
        raise exceptions.UserHasAlreadyActiveDeposit()

    deposit = models.Deposit(
        version=1,
        type=models.DepositType.GRANT_17_18,
        amount=decimal.Decimal(0),
        source=deposit_source,
        user=beneficiary,
        expirationDate=compute_deposit_expiration_date(beneficiary, models.DepositType.GRANT_17_18),
    )
    db.session.add(deposit)
    db.session.flush()

    latest_recredit = _recredit_user(beneficiary)
    if latest_recredit:
        return latest_recredit.deposit

    return deposit


def create_deposit_v2(
    beneficiary: users_models.User,
    deposit_source: str,
    eligibility: users_models.EligibilityType,
) -> models.Deposit:
    """Create a new deposit for the user if there is no deposit yet."""
    from pcapi.core.users import eligibility_api

    age_at_registration = eligibility_api.get_age_at_first_registration(beneficiary, eligibility)
    granted_deposit = get_granted_deposit(beneficiary, eligibility, age_at_registration)
    if not granted_deposit:
        raise exceptions.UserNotGrantable()

    if repository.deposit_exists_for_beneficiary_and_type(beneficiary, granted_deposit.type):
        raise exceptions.DepositTypeAlreadyGrantedException(granted_deposit.type)

    if beneficiary.has_active_deposit:
        raise exceptions.UserHasAlreadyActiveDeposit()

    deposit = models.Deposit(
        version=granted_deposit.version,
        type=granted_deposit.type,
        amount=granted_deposit.amount,
        source=deposit_source,
        user=beneficiary,
        expirationDate=granted_deposit.expiration_date,
    )
    db.session.add(deposit)
    db.session.flush()

    # Edge-case: Validation of the registration occurred over one or two birthdays
    # Then we need to add recredit to compensate
    if (
        eligibility == users_models.EligibilityType.UNDERAGE
        and _can_be_recredited(beneficiary)
        and beneficiary.age
        and age_at_registration
    ):
        latest_recredit = _recredit_user(beneficiary)
        if latest_recredit:
            return latest_recredit.deposit

    return deposit


def expire_current_deposit_for_user(user: users_models.User) -> None:
    models.Deposit.query.filter(
        models.Deposit.user == user,
        models.Deposit.expirationDate > datetime.datetime.utcnow(),
    ).update(
        {
            models.Deposit.expirationDate: datetime.datetime.utcnow() - datetime.timedelta(minutes=5),
            models.Deposit.dateUpdated: datetime.datetime.utcnow(),
        },
    )
    db.session.flush()


def _can_be_recredited(user: users_models.User, age: int | None = None) -> bool:
    if age is None:
        age = user.age
    if feature.FeatureToggle.WIP_ENABLE_CREDIT_V3.is_active():
        return _can_be_recredited_v3(user, age)
    return _can_be_recredited_v2(user, age)


def _can_be_recredited_v2(user: users_models.User, age: int | None = None) -> bool:
    return (
        age in conf.RECREDIT_TYPE_AGE_MAPPING
        and _has_celebrated_birthday_since_credit_or_registration(user)
        and not _has_been_recredited(user, age)
    )


def _can_be_recredited_v3(user: users_models.User, age: int | None = None) -> bool:
    if age is None:
        return False
    if age < 16:
        return False
    if age not in conf.RECREDIT_TYPE_AGE_MAPPING:
        return False

    if not user.has_active_deposit:
        return False
    assert user.deposit is not None  # always True after the check above. Helps mypy.

    if user.deposit.type == models.DepositType.GRANT_18:
        return False

    # Handle old-new deposits transition
    if user.deposit.type == models.DepositType.GRANT_15_17:
        # In this very case, it is OK to aggressively cut the recredit at the exact time of the decree
        # because the user already has a deposit, this means we are in an automatic recredit process, so the users can't be late
        if age == 16 and datetime.datetime.utcnow() > settings.CREDIT_V3_DECREE_DATETIME:
            return False
        return _can_be_recredited_v2(user, age)

    has_been_recredited = any(
        recredit.recreditType == conf.RECREDIT_TYPE_AGE_MAPPING[age] for recredit in user.deposit.recredits
    )
    return not has_been_recredited


def _has_celebrated_birthday_since_credit_or_registration(user: users_models.User) -> bool:
    from pcapi.core.users import eligibility_api

    latest_birthday_date = typing.cast(datetime.date, user.latest_birthday)
    if user.deposit and user.deposit.dateCreated and (user.deposit.dateCreated.date() < latest_birthday_date):
        return True

    first_registration_datetime = eligibility_api.get_first_eligible_registration_date(
        user, user.validatedBirthDate, users_models.EligibilityType.UNDERAGE
    )
    if first_registration_datetime is None:
        return False

    return first_registration_datetime.date() < latest_birthday_date


def _has_been_recredited(user: users_models.User, age: int | None = None) -> bool:
    if age is None:
        age = user.age

    if age is None:
        logger.error("Trying to check recredit for user that has no age", extra={"user_id": user.id})
        return False

    if user.deposit is None:
        return False

    known_age_at_deposit = _get_known_age_at_deposit(user)
    if known_age_at_deposit == age:
        return True

    if len(user.deposit.recredits) == 0:
        return False

    has_been_recredited = conf.RECREDIT_TYPE_AGE_MAPPING[age] in [
        recredit.recreditType for recredit in user.deposit.recredits
    ]
    if has_been_recredited:
        return True

    if age == 16:
        # This condition handles the following edge case:
        # - User started the activation workflow at 15 and finished it at 17.
        #   This used to create a deposit holding the total amount from 15 to 17 years old without creating
        #   the deposit for 16 years old in the database.
        # - When trying to unlock their 18 years old deposit, we receive a new (correct) value for their age.
        # - If this age is 16, no recredit happened (see 1st point) so we need a different check.
        #
        # This edge case is unlikely, but was introduced in e9b5f5e4.
        return user.deposit.amount == sum(conf.RECREDIT_TYPE_AMOUNT_MAPPING.values())

    return False


def _get_known_age_at_deposit(user: users_models.User) -> int | None:
    from pcapi.core.users import eligibility_api

    if user.deposit is None:
        return None

    known_birthday_at_deposit = eligibility_api.get_known_birthday_at_date(user, user.deposit.dateCreated)
    if known_birthday_at_deposit is None:
        return None

    first_registration_date = eligibility_api.get_first_eligible_registration_date(
        user, known_birthday_at_deposit, users_models.EligibilityType.UNDERAGE
    )
    if first_registration_date is not None:
        return users_utils.get_age_at_date(known_birthday_at_deposit, first_registration_date, user.departementCode)

    return users_utils.get_age_at_date(known_birthday_at_deposit, user.deposit.dateCreated, user.departementCode)


def recredit_users() -> None:
    if (
        feature.FeatureToggle.WIP_ENABLE_CREDIT_V3.is_active()
        and datetime.datetime.utcnow() > settings.CREDIT_V3_DECREE_DATETIME
    ):
        upper_date = datetime.datetime.utcnow() - relativedelta(years=17)
        lower_date = datetime.datetime.utcnow() - relativedelta(years=19)
    else:
        upper_date = datetime.datetime.utcnow() - relativedelta(years=16)
        lower_date = datetime.datetime.utcnow() - relativedelta(years=18)

    user_ids = [
        result
        for result, in (
            users_models.User.query.filter(users_models.User.has_underage_beneficiary_role)
            .filter(users_models.User.validatedBirthDate > lower_date)
            .filter(users_models.User.validatedBirthDate <= upper_date)
            .with_entities(users_models.User.id)
            .all()
        )
    ]

    start_index = 0
    while start_index < len(user_ids):
        recredit_users_by_id(user_ids[start_index : start_index + RECREDIT_UNDERAGE_USERS_BATCH_SIZE])
        start_index += RECREDIT_UNDERAGE_USERS_BATCH_SIZE


def recredit_users_by_id(user_ids: list[int]) -> None:
    failed_users = []

    with transaction():
        users = (
            users_models.User.query.filter(users_models.User.id.in_(user_ids))
            .options(sa_orm.selectinload(users_models.User.deposits).selectinload(models.Deposit.recredits))
            .populate_existing()
            .with_for_update()
            .all()
        )
        users_to_recredit = [user for user in users if user.deposit and _can_be_recredited(user)]
        for user in users_to_recredit:
            try:
                recredit_user_if_no_missing_step(user)
            except exceptions.UserHasNotFinishedSubscription:
                continue
            except Exception as e:  # pylint: disable=broad-except
                failed_users.append(user.id)
                logger.exception("Could not recredit user %s: %s", user.id, e)
                continue

    logger.info("Recredited %s underage users deposits", len(users_to_recredit))
    if failed_users:
        logger.error("Failed to recredit %s users: %s", len(failed_users), failed_users)


def recredit_user_if_no_missing_step(user: users_models.User) -> None:
    from pcapi.core.subscription.api import get_user_subscription_state
    from pcapi.core.subscription.models import SubscriptionItemStatus

    if not user.eligibility:
        raise exceptions.UserCannotBeRecredited("User is not eligible for deposit")

    if not user.deposit:
        raise exceptions.UserCannotBeRecredited("User deposit was not created")

    subscription_state = get_user_subscription_state(user)
    if not (subscription_state.next_step is None and subscription_state.fraud_status == SubscriptionItemStatus.OK):
        raise exceptions.UserHasNotFinishedSubscription()

    recredit = _recredit_user(user)
    if not recredit:
        raise exceptions.UserCannotBeRecredited("Failed to recredit user")
    if recredit.recreditType == models.RecreditType.RECREDIT_18:
        user.remove_underage_beneficiary_role()
        user.add_beneficiary_role()

    user.recreditAmountToShow = recredit.amount if recredit.amount > 0 else None
    db.session.add(user)

    external_attributes_api.update_external_user(user)
    push_notifications.track_account_recredited(user.id, user.deposit, len(user.deposits))
    if feature.FeatureToggle.WIP_ENABLE_CREDIT_V3.is_active() and recredit.amount > 0:
        if user.age and user.age >= users_constants.ELIGIBILITY_AGE_18:
            # After the decree, send email to 18 years old users only
            # This email will hold information about the recredit after 18 years old specifics
            transactional_mails.send_recredit_email_to_18_years_old(user)
    if not feature.FeatureToggle.WIP_ENABLE_CREDIT_V3.is_active() and recredit.amount > 0:
        # This email will not be sent after the decree.
        # It will be handled by the email sent to the user for their birthday
        from pcapi.core.users import api as users_api

        domains_credit = users_api.get_domains_credit(user)
        transactional_mails.send_recredit_email_to_underage_beneficiary(user, recredit.amount, domains_credit)


def get_latest_age_related_user_recredit(user: users_models.User) -> models.Recredit | None:
    """
    This function assumes that the user.deposits and the deposit.recredits relationships are already loaded.

    Example: User.query.options(selectinload(User.deposits).selectinload(Deposit.recredits))
    """
    if not user.deposit:
        return None

    if user.deposit.type == models.DepositType.GRANT_17_18:
        recredit_types = [models.RecreditType.RECREDIT_18, models.RecreditType.RECREDIT_17]
    elif user.deposit.type == models.DepositType.GRANT_15_17:
        recredit_types = [
            models.RecreditType.RECREDIT_17,
            models.RecreditType.RECREDIT_16,
            models.RecreditType.RECREDIT_15,
        ]
    else:
        return None

    for recredit_type in recredit_types:
        latest_age_recredit = next(
            (recredit for recredit in user.deposit.recredits if recredit_type == recredit.recreditType), None
        )
        if latest_age_recredit:
            return latest_age_recredit

    return None
