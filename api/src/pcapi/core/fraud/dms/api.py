import logging

import pcapi.core.fraud.api as fraud_api
import pcapi.core.fraud.models as fraud_models
import pcapi.core.users.models as users_models
from pcapi.repository import repository


logger = logging.getLogger(__name__)


def get_fraud_check(user: users_models.User, application_number: int) -> fraud_models.BeneficiaryFraudCheck | None:
    return (
        fraud_models.BeneficiaryFraudCheck.query.filter(
            fraud_models.BeneficiaryFraudCheck.user == user,
            fraud_models.BeneficiaryFraudCheck.type == fraud_models.FraudCheckType.DMS,
            fraud_models.BeneficiaryFraudCheck.thirdPartyId == str(application_number),
        )
        .order_by(fraud_models.BeneficiaryFraudCheck.id.desc())
        .first()
    )


def create_fraud_check(
    user: users_models.User,
    application_number: int,
    source_data: fraud_models.DMSContent | None,
) -> fraud_models.BeneficiaryFraudCheck:
    eligibility_type = (
        fraud_api.decide_eligibility(user, source_data.get_birth_date(), source_data.get_registration_datetime())
        if source_data
        else None
    )
    fraud_check = fraud_models.BeneficiaryFraudCheck(
        user=user,
        type=fraud_models.FraudCheckType.DMS,
        thirdPartyId=str(application_number),
        resultContent=source_data.dict() if source_data else None,
        status=fraud_models.FraudCheckStatus.STARTED,
        eligibilityType=eligibility_type,
    )
    repository.save(fraud_check)
    return fraud_check
