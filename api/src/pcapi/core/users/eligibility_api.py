import datetime

from dateutil.relativedelta import relativedelta

from pcapi import settings
from pcapi.core.finance.models import DepositType
from pcapi.core.fraud import models as fraud_models
from pcapi.core.history import models as history_models
from pcapi.core.users import constants
from pcapi.core.users import models as users_models
from pcapi.core.users import utils as users_utils
from pcapi.models.feature import FeatureToggle
from pcapi.utils import date as date_utils

from . import exceptions


class EligibilityError(Exception):
    pass


def decide_eligibility(
    user: users_models.User,
    birth_date: datetime.date | None,
    at_datetime: datetime.datetime | None = None,
) -> users_models.EligibilityType | None:
    """
    This function assumes that the user.beneficiaryFraudChecks relationship is already loaded.
    """
    if birth_date is None:
        return None

    if at_datetime is None:
        at_datetime = datetime.datetime.utcnow()

    current_age = users_utils.get_age_from_birth_date(birth_date, user.departementCode)
    if not (15 <= current_age <= 20):
        return None

    eligibility_at_datetime = get_eligibility_at_date(birth_date, at_datetime, user.departementCode)
    if eligibility_at_datetime and eligibility_at_datetime != users_models.EligibilityType.FREE:
        return eligibility_at_datetime

    pre_decree_eligibility = get_pre_decree_eligibility(user, birth_date, at_datetime)
    if pre_decree_eligibility:
        return pre_decree_eligibility
    if eligibility_at_datetime:
        return eligibility_at_datetime

    first_age_17_to_18_registration_date = get_first_eligible_registration_date(
        user, birth_date, users_models.EligibilityType.AGE17_18
    )
    if first_age_17_to_18_registration_date:
        return get_eligibility_at_date(birth_date, first_age_17_to_18_registration_date, user.departementCode)

    current_eligibility = get_eligibility_at_date(birth_date, datetime.datetime.utcnow(), user.departementCode)
    return current_eligibility


def get_pre_decree_or_current_eligibility(user: users_models.User) -> users_models.EligibilityType | None:
    pre_decree_eligibility = get_pre_decree_eligibility(user, user.birth_date, datetime.datetime.utcnow())
    return pre_decree_eligibility or user.eligibility


def get_pre_decree_eligibility(
    user: users_models.User, birth_date: datetime.date, at_datetime: datetime.datetime
) -> users_models.EligibilityType | None:
    age = users_utils.get_age_at_date(birth_date, at_datetime, user.departementCode)
    if 18 <= age <= 19:
        pre_decree_eligibility = users_models.EligibilityType.AGE18
    elif 15 <= age <= 17:
        pre_decree_eligibility = users_models.EligibilityType.UNDERAGE
    else:
        return None

    first_registration_date = get_first_eligible_registration_date(user, birth_date, pre_decree_eligibility)
    if first_registration_date:
        return get_eligibility_at_date(birth_date, first_registration_date, user.departementCode)

    return None


def get_age_at_first_registration(user: users_models.User, eligibility: users_models.EligibilityType) -> int | None:
    if not user.birth_date:
        return None

    first_registration_date = get_first_eligible_registration_date(user, user.birth_date, eligibility)
    if not first_registration_date:
        return user.age

    age_at_registration = users_utils.get_age_at_date(user.birth_date, first_registration_date, user.departementCode)
    if (
        eligibility == users_models.EligibilityType.UNDERAGE
        and age_at_registration not in constants.ELIGIBILITY_UNDERAGE_RANGE
    ):
        return None
    return age_at_registration


def get_first_eligible_registration_date(
    user: users_models.User,
    birth_date: datetime.date | None,
    eligibility: users_models.EligibilityType | None = None,
) -> datetime.datetime | None:
    fraud_checks = user.beneficiaryFraudChecks
    if not fraud_checks or not birth_date:
        return None

    registration_dates = sorted(
        fraud_check.get_min_date_between_creation_and_registration()
        for fraud_check in fraud_checks
        if (not eligibility or fraud_check.eligibilityType == eligibility)
    )
    for registration_date in registration_dates:
        eligibility_at_date = get_eligibility_at_date(birth_date, registration_date, user.departementCode)
        if eligibility is None and eligibility_at_date is not None:
            return registration_date

        if eligibility is not None and eligibility_at_date == eligibility:
            return registration_date

    return None


def get_eligibility_at_date(
    birth_date: datetime.date, at_datetime: datetime.datetime, department_code: str | None = None
) -> users_models.EligibilityType | None:
    if not is_datetime_within_eligibility_period(birth_date, at_datetime, department_code):
        return None

    age = users_utils.get_age_at_date(birth_date, at_datetime, department_code)

    if at_datetime < settings.CREDIT_V3_DECREE_DATETIME:
        if age in constants.ELIGIBILITY_UNDERAGE_RANGE:
            return users_models.EligibilityType.UNDERAGE
        if constants.ELIGIBILITY_AGE_18 == age:
            return users_models.EligibilityType.AGE18

    if 17 <= age <= 18:
        return users_models.EligibilityType.AGE17_18

    if FeatureToggle.WIP_FREE_ELIGIBILITY.is_active() and 15 <= age <= 16:
        return users_models.EligibilityType.FREE

    return None


def is_datetime_within_eligibility_period(
    birth_date: datetime.date, at_datetime: datetime.datetime, department_code: str | None = None
) -> bool:
    tz_aware_datetime = at_datetime
    if not tz_aware_datetime.tzinfo:
        tz_aware_datetime = tz_aware_datetime.replace(tzinfo=datetime.timezone.utc)

    eligibility_start = get_eligibility_start_datetime(birth_date, at_datetime, department_code)
    eligibility_end = get_eligibility_end_datetime(birth_date, department_code)
    if (
        not birth_date
        or not eligibility_start
        or not eligibility_end
        or not (eligibility_start <= tz_aware_datetime < eligibility_end)
    ):
        return False

    return True


def get_eligibility_start_datetime(
    date_of_birth: datetime.date | datetime.datetime | None,
    at_datetime: datetime.datetime,
    department_code: str | None = None,
) -> datetime.datetime | None:
    if not date_of_birth:
        return None

    date_of_birth = date_utils.to_department_midnight(date_of_birth, department_code)
    fifteenth_birthday = date_of_birth + relativedelta(years=constants.ELIGIBILITY_UNDERAGE_RANGE[0])
    seventeenth_birthday = date_of_birth + relativedelta(years=17)

    if at_datetime < settings.CREDIT_V3_DECREE_DATETIME or FeatureToggle.WIP_FREE_ELIGIBILITY.is_active():
        return fifteenth_birthday

    return seventeenth_birthday


def get_eligibility_end_datetime(
    date_of_birth: datetime.date | datetime.datetime | None, department_code: str | None = None
) -> datetime.datetime | None:
    if not date_of_birth:
        return None

    date_of_birth = date_utils.to_department_midnight(date_of_birth, department_code)
    nineteenth_birthday = date_of_birth + relativedelta(years=19)
    return nineteenth_birthday


def is_eligibility_activable(user: users_models.User, eligibility: users_models.EligibilityType | None) -> bool:
    return (
        user.eligibility == eligibility
        and is_eligible_for_next_recredit_activation_steps(user)
        and is_user_age_compatible_with_eligibility(user.age, eligibility)
    )


def is_eligible_for_next_recredit_activation_steps(user: users_models.User) -> bool:
    if not user.is_beneficiary:
        return user.is_eligible

    if user.has_beneficiary_role:
        return False

    if user.has_underage_beneficiary_role:
        return user.is_18_or_above_eligible

    if user.has_free_beneficiary_role:
        return user.is_underage_eligible or user.is_18_or_above_eligible

    return False


def is_user_age_compatible_with_eligibility(
    user_age: int | None, eligibility: users_models.EligibilityType | None
) -> bool:
    if not user_age:
        return False
    if eligibility == users_models.EligibilityType.UNDERAGE:
        return user_age in constants.ELIGIBILITY_UNDERAGE_RANGE
    if eligibility == users_models.EligibilityType.AGE18:
        return user_age >= constants.ELIGIBILITY_AGE_18
    if eligibility == users_models.EligibilityType.AGE17_18:
        return user_age >= 17
    return False


def is_underage_eligibility(eligibility: users_models.EligibilityType | None, age: int | None) -> bool:
    if eligibility == users_models.EligibilityType.UNDERAGE:
        return True

    if eligibility == users_models.EligibilityType.AGE17_18 and age:
        return age < 18

    return False


def is_18_or_above_eligibility(eligibility: users_models.EligibilityType | None, age: int | None) -> bool:
    if eligibility == users_models.EligibilityType.AGE18:
        return True

    if eligibility == users_models.EligibilityType.AGE17_18 and age:
        return age >= 18

    return False


def get_known_birthday_at_date(user: users_models.User, at_date: datetime.datetime) -> datetime.date | None:
    """Finds the birth date of the user at the given date, as the app would have known it at that time.

    Args:
        user (users_models.User): user
        at_date (datetime.datetime): date at which to find the presumed birth date

    Returns:
        datetime.date | None: the birth date of the user at the given date, or None if no birth date is found
    """

    identity_provider_birthday_checks = [
        fraud_check
        for fraud_check in user.beneficiaryFraudChecks
        if fraud_check.status == fraud_models.FraudCheckStatus.OK
        and fraud_check.get_identity_check_birth_date() is not None
        and fraud_check.dateCreated < at_date
    ]
    last_identity_provider_birthday_check = max(
        identity_provider_birthday_checks, key=lambda check: check.dateCreated, default=None
    )

    birthday_actions = [
        action
        for action in user.action_history
        if action.actionType == history_models.ActionType.INFO_MODIFIED
        and action.extraData
        and "modified_info" in action.extraData
        and action.extraData["modified_info"].get("validatedBirthDate") is not None
        and action.actionDate < at_date
    ]
    last_birthday_action = max(birthday_actions, key=lambda action: action.actionDate, default=None)

    known_birthday_at_date: datetime.date | None = None
    match last_identity_provider_birthday_check, last_birthday_action:
        case None, None:
            if user.dateOfBirth is None:
                return None
            known_birthday_at_date = user.dateOfBirth.date()

        case check, None:
            assert check is not None
            known_birthday_at_date = check.get_identity_check_birth_date()

        case None, action:
            assert action is not None
            known_birthday_at_date = datetime.datetime.strptime(
                action.extraData["modified_info"]["validatedBirthDate"]["new_info"], "%Y-%m-%d"
            ).date()

        case check, action:
            assert check is not None
            assert action is not None
            if check.dateCreated < action.actionDate:
                known_birthday_at_date = datetime.datetime.strptime(
                    action.extraData["modified_info"]["validatedBirthDate"]["new_info"], "%Y-%m-%d"
                ).date()
            else:
                known_birthday_at_date = check.get_identity_check_birth_date()

        case _:
            raise ValueError(
                f"unexpected {last_identity_provider_birthday_check = }, {last_birthday_action = } combination for user {user.id =}"
            )

    return known_birthday_at_date


def get_activated_eligibility(deposit_type: DepositType) -> users_models.EligibilityType:
    match deposit_type:
        case DepositType.GRANT_17_18:
            return users_models.EligibilityType.AGE17_18
        case DepositType.GRANT_15_17:
            return users_models.EligibilityType.UNDERAGE
        case DepositType.GRANT_18:
            return users_models.EligibilityType.AGE18
        case DepositType.GRANT_FREE:
            return users_models.EligibilityType.FREE
        case _:
            raise exceptions.UnknownDepositType(f"{deposit_type}")
