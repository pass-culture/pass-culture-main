import logging
from typing import Optional

import pcapi.core.fraud.api as fraud_api
import pcapi.core.fraud.models as fraud_models
import pcapi.core.users.models as users_models
import pcapi.repository as pcapi_repository


logger = logging.getLogger(__name__)


def get_fraud_check(
    user: users_models.User,
    application_id: int,
) -> Optional[fraud_models.BeneficiaryFraudCheck]:
    # replace with one_or_one once the data are cleaned up
    return (
        fraud_models.BeneficiaryFraudCheck.query.filter(
            fraud_models.BeneficiaryFraudCheck.user == user,
            fraud_models.BeneficiaryFraudCheck.type == fraud_models.FraudCheckType.DMS,
            fraud_models.BeneficiaryFraudCheck.thirdPartyId == str(application_id),
        )
        .order_by(fraud_models.BeneficiaryFraudCheck.id.desc())
        .first()
    )


def create_fraud_check(
    user: users_models.User,
    application_id: int,
    source_data: typing.Optional[fraud_models.DMSContent],
) -> fraud_models.BeneficiaryFraudCheck:
    eligibility_type = fraud_api.decide_eligibility(user, source_data) if source_data else None
    fraud_check = fraud_models.BeneficiaryFraudCheck(
        user=user,
        type=fraud_models.FraudCheckType.DMS,
        thirdPartyId=str(application_id),
        resultContent=source_data.dict() if source_data else None,
        status=fraud_models.FraudCheckStatus.STARTED,
        eligibilityType=eligibility_type,
    )
    return fraud_check


def get_or_create_fraud_check(
    user: users_models.User, application_id: int, result_content=None
) -> fraud_models.BeneficiaryFraudCheck:
    fraud_check = get_fraud_check(user, application_id)
    if fraud_check is None:
        return create_fraud_check(user, application_id, result_content)
    return fraud_check

