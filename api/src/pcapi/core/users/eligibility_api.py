import datetime

from dateutil.relativedelta import relativedelta

from pcapi import settings
from pcapi.core.users import constants
from pcapi.core.users import models as users_models
from pcapi.core.users import utils as users_utils
from pcapi.models.feature import FeatureToggle


class EligibilityError(Exception):
    pass


def decide_eligibility(
    user: users_models.User,
    birth_date: datetime.date | None,
    registration_datetime: datetime.datetime | None,
) -> users_models.EligibilityType | None:
    """Returns the applicable eligibility of the user.
    It may be the current eligibility of the user if the age is between 15 and 18, or it may be the eligibility AGE18
    if the user is over 19 and had previously tried to register when the age was 18.
    """
    if birth_date is None:
        return None

    if FeatureToggle.WIP_ENABLE_CREDIT_V3.is_active():
        return decide_v3_credit_eligibility(user, birth_date, registration_datetime)

    user_age_today = users_utils.get_age_from_birth_date(birth_date, user.departementCode)
    if user_age_today < 15:
        return None
    if user_age_today < 18:
        return users_models.EligibilityType.UNDERAGE
    if user_age_today == 18:
        return users_models.EligibilityType.AGE18

    eligibility_today = get_extended_eligibility_at_date(birth_date, datetime.datetime.utcnow(), user.departementCode)
    if eligibility_today == users_models.EligibilityType.AGE18:
        return users_models.EligibilityType.AGE18

    if user_age_today == 19:
        first_eligible_registration_datetime = get_first_eligible_registration_date(
            user, birth_date, users_models.EligibilityType.AGE18
        )
        if first_eligible_registration_datetime:
            return get_extended_eligibility_at_date(
                birth_date, first_eligible_registration_datetime, user.departementCode
            )

    return None


def decide_v3_credit_eligibility(
    user: users_models.User,
    birth_date: datetime.date,
    registration_datetime: datetime.datetime | None,
) -> users_models.EligibilityType | None:
    """
    An user eligibility determines what type of deposit can be granted.
    Returns the first eligibility found using:
    1. the age at registration_datetime
    2. the age at first registration, looking into the user's fraud checks
    3. the current age.

    This function assumes that the user.beneficiaryFraudChecks relation is already loaded.
    """
    user_age = users_utils.get_age_from_birth_date(birth_date, user.departementCode)
    if user_age < 15 or user_age > 20:
        return None

    eligibility: users_models.EligibilityType | None = None
    if registration_datetime:
        eligibility = get_eligibility_at_date(birth_date, registration_datetime, user.departementCode)
    if eligibility:
        return eligibility

    first_eligible_registration_datetime = get_first_eligible_registration_date(user, birth_date)
    if first_eligible_registration_datetime:
        return get_extended_eligibility_at_date(birth_date, first_eligible_registration_datetime, user.departementCode)

    if 17 <= user_age <= 18:
        eligibility = users_models.EligibilityType.AGE17_18

    return eligibility


def get_eligibility_at_date(
    birth_date: datetime.date, specified_datetime: datetime.datetime, department_code: str | None = None
) -> users_models.EligibilityType | None:
    age = users_utils.get_age_at_date(birth_date, specified_datetime, department_code)

    if specified_datetime < settings.CREDIT_V3_DECREE_DATETIME or not FeatureToggle.WIP_ENABLE_CREDIT_V3.is_active():
        if age in constants.ELIGIBILITY_UNDERAGE_RANGE:
            return users_models.EligibilityType.UNDERAGE
        if constants.ELIGIBILITY_AGE_18 == age:
            return users_models.EligibilityType.AGE18

    if FeatureToggle.WIP_ENABLE_CREDIT_V3.is_active() and 17 <= age <= 18:
        return users_models.EligibilityType.AGE17_18

    return None


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
        if (eligibility is None or fraud_check.eligibilityType == eligibility)
    )
    eligible_registration_dates = [
        registration_date
        for registration_date in registration_dates
        if get_extended_eligibility_at_date(birth_date, registration_date, user.departementCode) is not None
    ]
    if eligible_registration_dates:
        return eligible_registration_dates[0]

    return None


def get_extended_eligibility_at_date(
    date_of_birth: datetime.date | None, specified_datetime: datetime.datetime, department_code: str | None = None
) -> users_models.EligibilityType | None:
    """
    Extended eligibility means that this function considers a non-eligible user eligible,
    as long as they were eligible at the specified datetime

    This is summed up as this pseudocode:  eligibility_start < specified_datetime < eligibility_end
    """
    # TODO timezone these functions
    eligibility_start = get_eligibility_start_datetime(date_of_birth)
    eligibility_end = get_eligibility_end_datetime(date_of_birth)

    if not date_of_birth or not (eligibility_start <= specified_datetime < eligibility_end):  # type: ignore[operator]
        return None

    age = users_utils.get_age_at_date(date_of_birth, specified_datetime, department_code)
    if not age:
        return None

    if specified_datetime < settings.CREDIT_V3_DECREE_DATETIME or not FeatureToggle.WIP_ENABLE_CREDIT_V3.is_active():
        if age in constants.ELIGIBILITY_UNDERAGE_RANGE:
            return users_models.EligibilityType.UNDERAGE
        # If the user is older than 18 in UTC timezone, we consider them eligible until they reach eligibility_end
        if constants.ELIGIBILITY_AGE_18 <= age and specified_datetime < eligibility_end:  # type: ignore[operator]
            return users_models.EligibilityType.AGE18

    if FeatureToggle.WIP_ENABLE_CREDIT_V3.is_active() and age >= 17:
        return users_models.EligibilityType.AGE17_18

    return None


def get_eligibility_start_datetime(
    date_of_birth: datetime.date | datetime.datetime | None,
) -> datetime.datetime | None:
    if not date_of_birth:
        return None

    date_of_birth = datetime.datetime.combine(date_of_birth, datetime.time(0, 0))
    fifteenth_birthday = date_of_birth + relativedelta(years=constants.ELIGIBILITY_UNDERAGE_RANGE[0])

    return fifteenth_birthday


def get_eligibility_end_datetime(
    date_of_birth: datetime.date | datetime.datetime | None,
) -> datetime.datetime | None:
    if not date_of_birth:
        return None

    return datetime.datetime.combine(date_of_birth, datetime.time(0, 0)) + relativedelta(
        years=constants.ELIGIBILITY_AGE_18 + 1, hour=11
    )


def is_eligibility_activable(user: users_models.User, eligibility: users_models.EligibilityType | None) -> bool:
    return (
        user.eligibility == eligibility
        and is_eligible_for_next_recredit_activation_steps(user)
        and is_user_age_compatible_with_eligibility(user.age, eligibility)
    )


def is_eligible_for_next_recredit_activation_steps(user: users_models.User) -> bool:
    if not user.is_beneficiary:
        return user.is_eligible

    if not user.has_beneficiary_role:
        return user.is_18_or_above_eligible

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
