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
    source_data: fraud_models.DMSContent,
) -> fraud_models.BeneficiaryFraudCheck:
    application_id = str(source_data.application_id)
    eligibility_type = fraud_api.decide_eligibility(
        user, source_data.get_registration_datetime(), source_data.get_birth_date()
    )
    fraud_check = fraud_models.BeneficiaryFraudCheck(
        user=user,
        type=fraud_models.FraudCheckType.DMS,
        thirdPartyId=application_id,
        resultContent=source_data.dict(),
        status=fraud_models.FraudCheckStatus.STARTED,
        eligibilityType=eligibility_type,
    )
    pcapi_repository.repository.save(fraud_check)
    return fraud_check
