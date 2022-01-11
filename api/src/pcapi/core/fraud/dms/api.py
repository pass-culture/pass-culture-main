import logging
from typing import Optional

import pcapi.core.fraud.exceptions as fraud_exceptions
import pcapi.core.fraud.models as fraud_models
import pcapi.core.users.models as users_models
import pcapi.repository as pcapi_repository


logger = logging.getLogger(__name__)


def get_dms_fraud_check(
    user: users_models.User,
    application_id: str,
) -> Optional[fraud_models.BeneficiaryFraudCheck]:
    # replace with one_or_one once the data are cleaned up
    return (
        fraud_models.BeneficiaryFraudCheck.query.filter(
            fraud_models.BeneficiaryFraudCheck.user == user,
            fraud_models.BeneficiaryFraudCheck.type == fraud_models.FraudCheckType.DMS,
            fraud_models.BeneficiaryFraudCheck.thirdPartyId == application_id,
        )
        .order_by(fraud_models.BeneficiaryFraudCheck.id.desc())
        .first()
    )


def start_dms_fraud_check(
    user: users_models.User,
    source_data: fraud_models.DMSContent,
) -> fraud_models.BeneficiaryFraudCheck:
    application_id = str(source_data.application_id)
    fraud_check = get_dms_fraud_check(user, application_id)
    if not fraud_check:
        fraud_check = fraud_models.BeneficiaryFraudCheck(
            user=user,
            type=fraud_models.FraudCheckType.DMS,
            thirdPartyId=application_id,
            resultContent=source_data.dict(),
            status=fraud_models.FraudCheckStatus.PENDING,
            eligibilityType=source_data.get_eligibility_type(),
        )
        pcapi_repository.repository.save(fraud_check)

    if fraud_check.status != fraud_models.FraudCheckStatus.PENDING:
        raise fraud_exceptions.ApplicationValidationAlreadyStarted()

    return fraud_check
