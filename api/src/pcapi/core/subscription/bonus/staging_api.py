"""
Wrapper around the API Particulier connector that allows configuration of their
reponse through config BeneficiaryFraudChecks.
"""

import datetime

from pcapi.connectors import api_particulier
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription.bonus import schemas as bonus_schemas
from pcapi.core.users import models as users_models


def get_and_mock_quotient_familial(
    quotient_familial_fraud_check: subscription_models.BeneficiaryFraudCheck,
    at_date: datetime.date,
    user: users_models.user,
) -> api_particulier.QuotientFamilialResponse:
    bonus_credit_content = quotient_familial_fraud_check.source_data()
    if not isinstance(bonus_credit_content, bonus_schemas.QuotientFamilialBonusCreditContent):
        raise ValueError(f"BonusCreditContent was expected while {type(bonus_credit_content)} was given")

    mock_config = _get_last_quotient_familial_config(user)
    if not mock_config:
        return api_particulier.get_quotient_familial(bonus_credit_content.custodian, at_date)

    if not mock_config.http_status_code:
        raise ValueError("Mocked API Response calls must have a defined http_status_code")

    mocked_custodian = MOCK_CUSTODIAN_BY_HTTP_STATUS[mock_config.http_status_code]
    api_particulier_response = api_particulier.get_quotient_familial(mocked_custodian)

    api_particulier_response.data.enfants = [_build_api_enfants_response(child) for child in mock_config.children]
    return api_particulier_response


def _get_last_quotient_familial_config(
    user: users_models.User,
) -> bonus_schemas.QuotientFamilialBonusCreditContent | None:
    config_fraud_checks = [
        fraud_check
        for fraud_check in user.beneficiaryFraudChecks
        if fraud_check.type == subscription_models.FraudCheckType.QF_BONUS_CREDIT
        and fraud_check.status == subscription_models.FraudCheckStatus.MOCK_CONFIG
    ]
    if not config_fraud_checks:
        return None

    last_config = config_fraud_checks[-1]  # the user.beneficiaryFraudChecks relationship is ordered

    source_data = last_config.source_data()
    if not isinstance(source_data, bonus_schemas.QuotientFamilialBonusCreditContent):
        raise ValueError(f"BonusCreditContent was expected while {type(source_data)} was given")

    return source_data
