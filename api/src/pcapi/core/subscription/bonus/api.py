import logging

from dateutil.relativedelta import relativedelta

from pcapi.connectors import api_particulier
from pcapi.core.subscription import fraud_check_api
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription import schemas as subscription_schemas
from pcapi.core.subscription.bonus import schemas as bonus_schemas
from pcapi.core.users import models as users_models
from pcapi.utils.clean_accents import clean_accents
from pcapi.utils.transaction_manager import atomic


logger = logging.getLogger(__name__)

QUOTIENT_FAMILIAL_THRESHOLD = 3000


def apply_for_quotient_familial_bonus(quotient_familial_fraud_check: subscription_models.BeneficiaryFraudCheck) -> None:
    source_data = quotient_familial_fraud_check.source_data()
    if not isinstance(source_data, bonus_schemas.QuotientFamilialBonusCreditContent):
        raise ValueError(f"BonusCreditContent was expected while {type(source_data)} was given")

    user = quotient_familial_fraud_check.user
    quotient_familial_content: bonus_schemas.QuotientFamilialContent | None = None
    try:
        quotient_familial_content = _get_user_quotient_familial_content(source_data.custodian, user)
    except api_particulier.ParticulierApiQuotientFamilialNotFound:
        status = subscription_models.FraudCheckStatus.KO
        reason_codes = [subscription_models.FraudReasonCode.CUSTODIAN_NOT_FOUND]
    else:
        status, reason_codes = _get_credit_bonus_status(user, quotient_familial_content)

    with atomic():
        quotient_familial_fraud_check.status = status
        quotient_familial_fraud_check.reasonCodes = reason_codes

        if not quotient_familial_content:
            return

        _update_bonus_fraud_check_content(quotient_familial_fraud_check, quotient_familial_content)


def _get_user_quotient_familial_content(
    custodian: bonus_schemas.QuotientFamilialCustodian, user: users_models.User
) -> bonus_schemas.QuotientFamilialContent | None:
    """
    Calls the Quotient Familial API twelve times, deserializing the lowest one.
    Returns None if the custodian exists but the user was not found in the tax household.
    """
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

    if not quotient_familial_responses:
        return None

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
    id_fraud_check = fraud_check_api.get_last_filled_identity_fraud_check(user)
    if not id_fraud_check:
        raise ValueError(f"{user = } asked for credit bonus without validating their identity")

    id_source_data = id_fraud_check.source_data()
    if not isinstance(id_source_data, subscription_schemas.IdentityCheckContent):
        raise ValueError(f"Unexpected {id_fraud_check = } received instead of identity check")

    tax_household_children = quotient_familial_response.data.enfants
    for child in tax_household_children:
        has_first_name_match = _does_names_match(user.firstName, child.prenoms)
        has_last_name_match = _does_names_match(user.lastName, child.nom_naissance) or _does_names_match(
            user.lastName, child.nom_usage
        )
        has_birth_day_match = user.validatedBirthDate == child.date_naissance
        has_gender_match = id_source_data.get_civility() == child.sexe.value
        if has_first_name_match and has_last_name_match and has_birth_day_match and has_gender_match:
            return True

    return False


def _does_names_match(name_1: str | None, name_2: str | None) -> bool:
    if name_1 is None or name_2 is None:
        return False
    return clean_accents(name_1).upper() in clean_accents(name_2).upper()


def _get_credit_bonus_status(
    user: users_models.User, quotient_familial_content: bonus_schemas.QuotientFamilialContent | None
) -> tuple[subscription_models.FraudCheckStatus, list[subscription_models.FraudReasonCode]]:
    if not quotient_familial_content:
        return subscription_models.FraudCheckStatus.KO, [subscription_models.FraudReasonCode.NOT_IN_TAX_HOUSEHOLD]
    if quotient_familial_content.value > QUOTIENT_FAMILIAL_THRESHOLD:
        return subscription_models.FraudCheckStatus.KO, [subscription_models.FraudReasonCode.QUOTIENT_FAMILIAL_TOO_HIGH]
    return (subscription_models.FraudCheckStatus.OK, [])


def _update_bonus_fraud_check_content(
    fraud_check: subscription_models.BeneficiaryFraudCheck,
    quotient_familial_content: bonus_schemas.QuotientFamilialContent,
) -> None:
    if not fraud_check.resultContent:
        fraud_check.resultContent = {}
    if not fraud_check.resultContent.get("quotient_familial"):
        fraud_check.resultContent["quotient_familial"] = {}
    fraud_check.resultContent["quotient_familial"].update(**quotient_familial_content.model_dump())
