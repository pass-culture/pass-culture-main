import datetime
import random

from dateutil.relativedelta import relativedelta

from pcapi import settings
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription.bonus import constants as bonus_constants
from pcapi.core.subscription.bonus import schemas as bonus_schemas
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.utils import date as date_utils


def create_qf_bonus_credit_fraud_check(
    user: users_models.User,
    *,
    last_name: str,
    common_name: str | None = None,
    first_names: list[str],
    birth_date: datetime.date,
    gender: users_models.GenderEnum,
    birth_country_cog_code: str | None = None,
    birth_city_cog_code: str | None = None,
    origin: str,
) -> subscription_models.BeneficiaryFraudCheck:
    custodian = bonus_schemas.BonusCreditPerson(
        last_name=last_name,
        common_name=common_name,
        first_names=first_names,
        birth_date=birth_date,
        gender=gender,
        birth_country_cog_code=birth_country_cog_code,
        birth_city_cog_code=birth_city_cog_code,
    )
    next_retry_at = _get_next_bonus_credit_retry_date(origin)
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
) -> tuple[subscription_models.BeneficiaryFraudCheck, subscription_models.BeneficiaryFraudCheck]:
    eligibility = user.eligibility
    person = _build_bonus_credit_person_for_disability(user, birth_country_cog_code, birth_city_cog_code)
    next_retry_at = _get_next_bonus_credit_retry_date(origin)
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


def _get_next_bonus_credit_retry_date(bonus_credit_origin: str) -> datetime.datetime:
    """
    A next retry date is mandatory to ensure recovery in any edge cases.
    """
    is_bonus_automatic = bonus_credit_origin.startswith(bonus_constants.AUTOMATIC_ORIGIN)
    if not is_bonus_automatic:
        return date_utils.get_naive_utc_now() + relativedelta(days=1)

    # since only disability bonus credit attempts are created automatically, we need to add
    # a jitter to prevent guessing the origin of the bonus credit through its creation timing.
    jitter = random.randint(0, settings.BONUS_CREDIT_DELAY_JITTER)
    return date_utils.get_naive_utc_now() + relativedelta(seconds=settings.BONUS_CREDIT_DELAY + jitter)


def _build_bonus_credit_person_for_disability(
    user: users_models.User,
    birth_country_cog_code: str | None = None,
    birth_city_cog_code: str | None = None,
) -> bonus_schemas.BonusCreditPerson:

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


def accelerate_automatic_disability_bonus_fraud_checks(
    fraud_checks: list[subscription_models.BeneficiaryFraudCheck], new_origin: str
) -> list[subscription_models.BeneficiaryFraudCheck]:
    accelerated_fraud_checks = []
    for fraud_check in fraud_checks:
        if fraud_check.reason is None:
            continue

        disability_bonus_types = [
            subscription_models.FraudCheckType.AAH_BONUS_CREDIT,
            subscription_models.FraudCheckType.AEEH_BONUS_CREDIT,
        ]
        is_pending_automatic_fraud_check = (
            fraud_check.type in disability_bonus_types
            and fraud_check.status == subscription_models.FraudCheckStatus.STARTED
            and fraud_check.reason.startswith(bonus_constants.AUTOMATIC_ORIGIN)
        )
        if not is_pending_automatic_fraud_check:
            continue

        fraud_check.reason = fraud_check.reason + f", accelerated by {new_origin}"

        if not fraud_check.resultContent:
            fraud_check.resultContent = {}
        fraud_check.resultContent["next_retry_at"] = date_utils.get_naive_utc_now() + relativedelta(days=1)

        accelerated_fraud_checks.append(fraud_check)

    return accelerated_fraud_checks
