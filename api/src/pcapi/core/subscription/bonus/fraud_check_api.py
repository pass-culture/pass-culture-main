import datetime

from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription.bonus import schemas as bonus_schemas
from pcapi.core.users import models as users_models
from pcapi.models import db


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
    fraud_check_content = bonus_schemas.QuotientFamilialBonusCreditContent(custodian=custodian)

    fraud_check = subscription_models.BeneficiaryFraudCheck(
        user=user,
        type=subscription_models.FraudCheckType.QF_BONUS_CREDIT,
        status=subscription_models.FraudCheckStatus.STARTED,
        reason=origin,
        thirdPartyId=f"qf-bonus-credit-{user.id}",
        resultContent=fraud_check_content.model_dump(exclude_unset=True),
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
    aah_fraud_check_content = bonus_schemas.AdultDisabilityBonusCreditContent(person=person)

    aah_fraud_check = subscription_models.BeneficiaryFraudCheck(
        user=user,
        type=subscription_models.FraudCheckType.AAH_BONUS_CREDIT,
        status=subscription_models.FraudCheckStatus.STARTED,
        reason=origin,
        thirdPartyId=f"aah-bonus-credit-{user.id}",
        resultContent=aah_fraud_check_content.model_dump(exclude_unset=True),
        eligibilityType=eligibility,
    )
    db.session.add(aah_fraud_check)

    aeeh_fraud_check_content = bonus_schemas.DisabledChildEducationBonusCreditContent(person=person)
    aeeh_fraud_check = subscription_models.BeneficiaryFraudCheck(
        user=user,
        type=subscription_models.FraudCheckType.AEEH_BONUS_CREDIT,
        status=subscription_models.FraudCheckStatus.STARTED,
        reason=origin,
        thirdPartyId=f"aeeh-bonus-credit-{user.id}",
        resultContent=aeeh_fraud_check_content.model_dump(exclude_unset=True),
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
