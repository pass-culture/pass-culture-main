import datetime

from dateutil.relativedelta import relativedelta

from pcapi import settings
from pcapi.core.finance import models as finance_models
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription.bonus import constants as bonus_constants
from pcapi.core.subscription.bonus import schemas as bonus_schemas
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.utils import date as date_utils


def get_bonus_credit_fraud_checks(
    user: users_models.User,
    fraud_check_type: subscription_models.FraudCheckType | None = None,
    excluded_origin: str | None = None,
) -> list[subscription_models.BeneficiaryFraudCheck]:
    if fraud_check_type:
        allowed_fraud_check_types = [fraud_check_type]
    else:
        allowed_fraud_check_types = [
            subscription_models.FraudCheckType.AAH_BONUS_CREDIT,
            subscription_models.FraudCheckType.AEEH_BONUS_CREDIT,
            subscription_models.FraudCheckType.QF_BONUS_CREDIT,
        ]

    # `user.beneficiaryFraudChecks` are ordered by creation date
    bonus_fraud_checks = [
        fraud_check
        for fraud_check in user.beneficiaryFraudChecks
        if fraud_check.type in allowed_fraud_check_types
        and fraud_check.status != subscription_models.FraudCheckStatus.MOCK_CONFIG
    ]
    if excluded_origin is None:
        return bonus_fraud_checks

    return [
        fraud_check
        for fraud_check in bonus_fraud_checks
        if not (fraud_check.reason and fraud_check.reason.startswith(excluded_origin))
    ]


def create_qf_bonus_credit_fraud_check(
    user: users_models.User,
    *,
    last_name: str | None = None,
    common_name: str | None = None,
    first_names: list[str] | None = None,
    birth_date: datetime.date | None = None,
    gender: users_models.GenderEnum | None = None,
    birth_country_cog_code: str | None = None,
    birth_city_cog_code: str | None = None,
    origin: str,
) -> subscription_models.BeneficiaryFraudCheck:
    if not last_name and user.lastName:
        last_name = user.lastName
    if not last_name:
        raise ValueError("A last name was expected")

    if not first_names and user.firstName:
        first_names = [user.firstName]
    if not first_names:
        raise ValueError("A first name was expected")

    if not birth_date and user.validatedBirthDate:
        birth_date = user.validatedBirthDate
    if not birth_date:
        raise ValueError("A birth date was expected")

    if not gender and user.gender:
        gender = user.gender
    if not gender:
        raise ValueError("A gender was expected")

    birth_location_kwargs: dict[str, str | None] = {"birth_country_cog_code": birth_country_cog_code}
    if birth_city_cog_code:
        birth_location_kwargs["birth_city_cog_code"] = birth_city_cog_code
    else:
        birth_location_kwargs["birth_city"] = user.birthPlace

    custodian = bonus_schemas.BonusCreditPerson(
        last_name=last_name,
        common_name=common_name,
        first_names=first_names,
        birth_date=birth_date,
        gender=gender,
        **{key: value for key, value in birth_location_kwargs.items() if value},
    )

    next_retry_at = date_utils.get_naive_utc_now() + relativedelta(days=1)
    fraud_check_content = bonus_schemas.QuotientFamilialBonusCreditContent(
        custodian=custodian, next_retry_at=next_retry_at
    )

    fraud_check = subscription_models.BeneficiaryFraudCheck(
        user=user,
        type=subscription_models.FraudCheckType.QF_BONUS_CREDIT,
        status=subscription_models.FraudCheckStatus.STARTED,
        reason=origin,
        thirdPartyId=f"qf-bonus-credit-{user.id}",
        resultContent=fraud_check_content.model_dump(mode="json", exclude_unset=True),
        eligibilityType=user.eligibility,
    )
    db.session.add(fraud_check)
    db.session.flush()

    return fraud_check


def create_disability_bonus_credit_fraud_checks(
    user: users_models.User,
    *,
    birth_country_cog_code: str | None = None,
    birth_city_cog_code: str | None = None,
    origin: str,
    next_retry_at: datetime.datetime | None = None,
) -> tuple[subscription_models.BeneficiaryFraudCheck, subscription_models.BeneficiaryFraudCheck]:
    eligibility = user.eligibility
    person = _build_bonus_credit_person_for_disability(user, birth_country_cog_code, birth_city_cog_code)
    if not next_retry_at:
        next_retry_at = date_utils.get_naive_utc_now() + relativedelta(days=1)
    aah_fraud_check_content = bonus_schemas.AdultDisabilityBonusCreditContent(
        person=person, next_retry_at=next_retry_at
    )

    aah_fraud_check = subscription_models.BeneficiaryFraudCheck(
        user=user,
        type=subscription_models.FraudCheckType.AAH_BONUS_CREDIT,
        status=subscription_models.FraudCheckStatus.STARTED,
        reason=origin,
        thirdPartyId=f"aah-bonus-credit-{user.id}",
        resultContent=aah_fraud_check_content.model_dump(mode="json", exclude_unset=True),
        eligibilityType=eligibility,
    )
    db.session.add(aah_fraud_check)

    aeeh_fraud_check_content = bonus_schemas.DisabledChildEducationBonusCreditContent(
        person=person, next_retry_at=next_retry_at
    )
    aeeh_fraud_check = subscription_models.BeneficiaryFraudCheck(
        user=user,
        type=subscription_models.FraudCheckType.AEEH_BONUS_CREDIT,
        status=subscription_models.FraudCheckStatus.STARTED,
        reason=origin,
        thirdPartyId=f"aeeh-bonus-credit-{user.id}",
        resultContent=aeeh_fraud_check_content.model_dump(mode="json", exclude_unset=True),
        eligibilityType=eligibility,
    )
    db.session.add(aeeh_fraud_check)
    db.session.flush()

    return aah_fraud_check, aeeh_fraud_check


def _build_bonus_credit_person_for_disability(
    user: users_models.User,
    birth_country_cog_code: str | None = None,
    birth_city_cog_code: str | None = None,
) -> bonus_schemas.BonusCreditPerson:
    if not user.lastName:
        raise ValueError("User is expected to have a last name")

    if not user.firstName:
        raise ValueError("User is expected to have a first name")

    if not user.birth_date:
        raise ValueError("User is expected to have a birth date")

    birth_location_kwargs: dict[str, str | None] = {"birth_country_cog_code": birth_country_cog_code}
    if birth_city_cog_code:
        birth_location_kwargs["birth_city_cog_code"] = birth_city_cog_code
    else:
        birth_location_kwargs["birth_city"] = user.birthPlace

    return bonus_schemas.BonusCreditPerson(
        last_name=user.lastName,
        first_names=[user.firstName],
        birth_date=user.birth_date,
        gender=user.gender or users_models.GenderEnum.F,
        **{key: value for key, value in birth_location_kwargs.items() if value},
    )


def get_first_manual_attempt(user: users_models.User) -> subscription_models.BeneficiaryFraudCheck | None:
    return next(
        (
            fraud_check
            for fraud_check in user.beneficiaryFraudChecks
            if fraud_check.type in subscription_models.BONUS_CREDIT_CHECK_TYPES
            and fraud_check.reason
            and fraud_check.reason.startswith(bonus_constants.MANUAL_FORM_ENDPOINT_ORIGINS)
        ),
        None,
    )


def get_attempt_delay_in_seconds(fraud_check: subscription_models.BeneficiaryFraudCheck) -> int | None:
    eighteenth_recredit_date = _get_eighteenth_recredit_date(fraud_check.user)
    if eighteenth_recredit_date is None:
        return None

    can_fill_bonus_credit_form_since = max(eighteenth_recredit_date, settings.BONUS_CREDIT_DEPLOYMENT_DATETIME)
    elapsed_seconds = int((fraud_check.dateCreated - can_fill_bonus_credit_form_since).total_seconds())
    return elapsed_seconds


def _get_eighteenth_recredit_date(user: users_models.User) -> datetime.datetime | None:
    deposit = user.deposit
    if not deposit:
        return None

    eighteenth_recredits = [
        recredit for recredit in deposit.recredits if recredit.recreditType == finance_models.RecreditType.RECREDIT_18
    ]
    if not eighteenth_recredits:
        return None

    return min(recredit.dateCreated for recredit in eighteenth_recredits)


def count_manual_attempts(user: users_models.User, bonus_type: subscription_models.FraudCheckType | None = None) -> int:
    """
    Counts how many times the beneficiary filled a bonus credit form manually. Automatic and backoffice attempts are left out.
    """
    if bonus_type is None:
        bonus_types = [
            subscription_models.FraudCheckType.QF_BONUS_CREDIT,
            subscription_models.FraudCheckType.AAH_BONUS_CREDIT,
        ]
    else:
        bonus_types = [bonus_type]
    return sum(
        1
        for fraud_check in user.beneficiaryFraudChecks
        if fraud_check.type in bonus_types
        and fraud_check.reason
        and fraud_check.reason.startswith(bonus_constants.MANUAL_FORM_ENDPOINT_ORIGINS)
    )


def delete_bonus_fraud_checks(user: users_models.User) -> None:
    """
    We delete every bonus fraud checks to avoid retro engineering which bonus credit was granted through which process
    (AAH/AEEH or QF).
    """
    bonus_fraud_checks = [
        fraud_check
        for fraud_check in user.beneficiaryFraudChecks
        if fraud_check.type in subscription_models.BONUS_CREDIT_CHECK_TYPES
    ]
    for fraud_check in bonus_fraud_checks:
        db.session.delete(fraud_check)

    db.session.flush()
