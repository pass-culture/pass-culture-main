import datetime

from dateutil.relativedelta import relativedelta

from pcapi.connectors import api_particulier
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription.bonus import schemas as bonus_schemas
from pcapi.core.users import models as users_models
from pcapi.models import db


def get_quotient_familial_bonus(previous_bonus_fraud_check: subscription_models.BeneficiaryFraudCheck) -> None:
    source_data = previous_bonus_fraud_check.source_data()
    if not isinstance(source_data, bonus_schemas.BonusCreditContent):
        raise ValueError(f"BonusCreditContent was expected while {type(source_data)} was given")

    user = previous_bonus_fraud_check.user
    quotient_familial_content = _get_user_quotient_familial_content(source_data.custodian, user)
    status, reason_codes = _get_credit_bonus_status(user, quotient_familial_content)

    new_bonus_credit_content = bonus_schemas.BonusCreditContent(
        custodian=source_data.custodian,
        quotient_familial=quotient_familial_content,
    )
    fraud_check = subscription_models.BeneficiaryFraudCheck(
        user=user,
        type=subscription_models.FraudCheckType.BONUS_CREDIT,
        status=status,
        reasonCodes=reason_codes,
        reason="from get_quotient_familial_bonus function call",
        thirdPartyId=previous_bonus_fraud_check.thirdPartyId,
        resultContent=new_bonus_credit_content.dict(),
        eligibilityType=user.eligibility,
    )
    db.session.add(fraud_check)


def _get_user_quotient_familial_content(
    custodian: bonus_schemas.QuotientFamilialCustodian, user: users_models.User
) -> bonus_schemas.QuotientFamilialContent:
    birth_date = user.validatedBirthDate
    if not birth_date:
        raise ValueError("Beneficiaries applying for the bonus are expected to have a non-null birth date")

    # the quotient familial is computed on the beneficiary's 17th year, not when the user is 17
    # that means we actually have to compute the quotient familial when the user is 16
    sixteenth_birthday = birth_date + relativedelta(years=16)

    quotient_familial_responses = []
    MONTHS_IN_A_YEAR = 12
    for month_offset in range(MONTHS_IN_A_YEAR):
        at_date = sixteenth_birthday + relativedelta(months=month_offset)
        quotient_familial_at_date = api_particulier.get_quotient_familial(
            last_name=custodian.last_name,
            first_names=custodian.first_names,
            common_name=custodian.common_name,
            birth_date=custodian.birth_date,
            gender=custodian.gender,
            country_insee_code=custodian.birth_country_cog_code,
            city_insee_code=custodian.birth_city_cog_code,
            quotient_familial_date=at_date,
        )

        if _is_user_part_of_tax_household(user, quotient_familial_at_date):
            quotient_familial_responses.append(quotient_familial_at_date)

    lowest_quotient_familial = min(quotient_familial_responses, key=lambda qf: qf.data.quotient_familial.valeur)
    return bonus_schemas.QuotientFamilialContent(
        provider=lowest_quotient_familial.data.quotient_familial.fournisseur,
        value=lowest_quotient_familial.data.quotient_familial.valeur,
        year=lowest_quotient_familial.data.quotient_familial.annee,
        month=lowest_quotient_familial.data.quotient_familial.mois,
        computation_year=lowest_quotient_familial.data.quotient_familial.annee_calcul,
        computation_month=lowest_quotient_familial.data.quotient_familial.mois_calcul,
    )


def _is_user_part_of_tax_household(
    user: users_models.User, quotient_familial_response: api_particulier.QuotientFamilialResponse
) -> bool:
    return True


def _get_credit_bonus_status(
    quotient_familial_content: bonus_schemas.QuotientFamilialContent, user: users_models.User
) -> tuple[subscription_models.FraudCheckStatus, list[subscription_models.FraudReasonCode] | None]:
    return (subscription_models.FraudCheckStatus.OK, None)
