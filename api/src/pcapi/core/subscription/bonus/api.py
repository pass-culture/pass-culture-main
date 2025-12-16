import logging

from dateutil.relativedelta import relativedelta

from pcapi import settings
from pcapi.connectors import api_particulier
from pcapi.core.finance import deposit_api
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription.bonus import constants as bonus_constants
from pcapi.core.subscription.bonus import schemas as bonus_schemas
from pcapi.core.subscription.bonus import staging_api
from pcapi.core.users import models as users_models
from pcapi.utils.clean_accents import clean_accents
from pcapi.utils.transaction_manager import atomic


logger = logging.getLogger(__name__)


def apply_for_quotient_familial_bonus(quotient_familial_fraud_check: subscription_models.BeneficiaryFraudCheck) -> None:
    """
    Gets the lowest Quotient Familial from the fraud check custodian, over the fraud check beneficiary seventeenth year,
    and updates the fraud check. Then gives the bonus recredit to the beneficiary if eligible.
    """
    user = quotient_familial_fraud_check.user
    if not deposit_api.can_receive_bonus_credit(user):
        return

    source_data = quotient_familial_fraud_check.source_data()
    if not isinstance(source_data, bonus_schemas.QuotientFamilialBonusCreditContent):
        raise ValueError(f"QuotientFamilialBonusCreditContent was expected while {type(source_data)} was given")

    quotient_familial_response: api_particulier.QuotientFamilialResponse | None = None
    try:
        quotient_familial_response = _get_user_quotient_familial_response(source_data.custodian, user)
    except api_particulier.ParticulierApiQuotientFamilialNotFound:
        status = subscription_models.FraudCheckStatus.KO
        reason_codes = [subscription_models.FraudReasonCode.CUSTODIAN_NOT_FOUND]
    else:
        status, reason_codes = _get_credit_bonus_status(user, quotient_familial_response.data)

    with atomic():
        quotient_familial_fraud_check.status = status
        quotient_familial_fraud_check.reasonCodes = reason_codes

        if not quotient_familial_response:
            return

        _update_bonus_fraud_check_content(quotient_familial_fraud_check, quotient_familial_response.data)

        if status != subscription_models.FraudCheckStatus.OK:
            return

        given_recredit = deposit_api.recredit_bonus_credit(user)
        if not given_recredit and deposit_api.can_receive_bonus_credit(user):
            logger.error(
                f"Failed to recredit user with bonus credit despite {status = } Quotient Familial fraud check",
                extra={"user_id": user.id, "beneficiary_fraud_check_id": quotient_familial_fraud_check.id},
            )

        if given_recredit:
            logger.info("Recredited user %s with bonus credit", user.id)


def _get_user_quotient_familial_response(
    custodian: bonus_schemas.QuotientFamilialCustodian, user: users_models.User
) -> api_particulier.QuotientFamilialResponse:
    """
    Calls the Quotient Familial API twelve times, returning the lowest one.
    """
    birth_date = user.validatedBirthDate
    if not birth_date:
        raise ValueError("Beneficiaries applying for the bonus are expected to have a non-null birth date")

    # the quotient familial is computed on the beneficiary's 17th year, not when the user is 17
    # that means we actually have to compute the quotient familial when the user is 16
    sixteenth_birthday = birth_date + relativedelta(years=16)

    all_quotient_familial_responses = []
    MONTHS_IN_A_YEAR = 12
    for month_offset in range(MONTHS_IN_A_YEAR):
        at_date = sixteenth_birthday + relativedelta(months=month_offset)

        if settings.ENABLE_PARTICULIER_API_MOCK:
            quotient_familial_at_date = staging_api.get_and_mock_quotient_familial(custodian, at_date, user)
        else:
            quotient_familial_at_date = api_particulier.get_quotient_familial(custodian, at_date)

        all_quotient_familial_responses.append(quotient_familial_at_date)

    quotients_familial_with_user = [
        qf for qf in all_quotient_familial_responses if _is_user_part_of_tax_household(user, qf.data.enfants)
    ]
    if quotients_familial_with_user:
        relevant_qf_responses = quotients_familial_with_user
    else:
        # we store the quotient familial even if the user does not seem to belong to the tax household,
        # to allow the support department to have the last say if the identity matching algorithm fails
        relevant_qf_responses = all_quotient_familial_responses

    lowest_quotient_familial = min(relevant_qf_responses, key=lambda qf: qf.data.quotient_familial.valeur)
    return lowest_quotient_familial


def _is_user_part_of_tax_household(
    user: users_models.User, tax_household_children: list[api_particulier.QuotientFamilialPerson]
) -> bool:
    for child in tax_household_children:
        has_first_name_match = _does_names_match(user.firstName, child.prenoms)
        has_last_name_match = _does_names_match(user.lastName, child.nom_naissance) or _does_names_match(
            user.lastName, child.nom_usage
        )
        has_birth_day_match = user.validatedBirthDate == child.date_naissance
        has_gender_match = user.gender == child.sexe

        if has_first_name_match and has_last_name_match and has_birth_day_match and has_gender_match:
            return True

    return False


def _does_names_match(name_1: str | None, name_2: str | None) -> bool:
    if name_1 is None or name_2 is None:
        return False
    return clean_accents(name_1).upper() in clean_accents(name_2).upper()


def _get_credit_bonus_status(
    user: users_models.User, quotient_familial_data: api_particulier.QuotientFamilialData
) -> tuple[subscription_models.FraudCheckStatus, list[subscription_models.FraudReasonCode]]:
    if not _is_user_part_of_tax_household(user, quotient_familial_data.enfants):
        return subscription_models.FraudCheckStatus.KO, [subscription_models.FraudReasonCode.NOT_IN_TAX_HOUSEHOLD]

    if quotient_familial_data.quotient_familial.valeur > bonus_constants.QUOTIENT_FAMILIAL_THRESHOLD:
        return subscription_models.FraudCheckStatus.KO, [subscription_models.FraudReasonCode.QUOTIENT_FAMILIAL_TOO_HIGH]

    return (subscription_models.FraudCheckStatus.OK, [])


def _update_bonus_fraud_check_content(
    fraud_check: subscription_models.BeneficiaryFraudCheck,
    quotient_familial_data: api_particulier.QuotientFamilialData,
) -> None:
    if not fraud_check.resultContent:
        fraud_check.resultContent = {}

    if not fraud_check.resultContent.get("quotient_familial"):
        fraud_check.resultContent["quotient_familial"] = {}

    quotient_familial_content = bonus_schemas.QuotientFamilialContent(
        provider=quotient_familial_data.quotient_familial.fournisseur,
        value=quotient_familial_data.quotient_familial.valeur,
        year=quotient_familial_data.quotient_familial.annee,
        month=quotient_familial_data.quotient_familial.mois,
        computation_year=quotient_familial_data.quotient_familial.annee_calcul,
        computation_month=quotient_familial_data.quotient_familial.mois_calcul,
    )
    fraud_check.resultContent["quotient_familial"].update(**quotient_familial_content.model_dump())

    tax_household_children = [
        bonus_schemas.QuotientFamilialChild(
            last_name=child.nom_naissance,
            common_name=child.nom_usage,
            first_names=child.prenoms.split(" ") if child.prenoms else [],
            birth_date=child.date_naissance,
            gender=child.sexe,
        )
        for child in quotient_familial_data.enfants
    ]
    fraud_check.resultContent["children"] = [child.model_dump() for child in tax_household_children]
