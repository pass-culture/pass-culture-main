from pcapi.core.fraud import models as fraud_models
from pcapi.core.users import models as users_models


def get_completed_profile_check(
    user: users_models.User, eligibility: users_models.EligibilityType | None
) -> fraud_models.BeneficiaryFraudCheck:
    return fraud_models.BeneficiaryFraudCheck.query.filter(
        fraud_models.BeneficiaryFraudCheck.user == user,
        fraud_models.BeneficiaryFraudCheck.type == fraud_models.FraudCheckType.PROFILE_COMPLETION,
        fraud_models.BeneficiaryFraudCheck.eligibilityType == eligibility,
        fraud_models.BeneficiaryFraudCheck.status == fraud_models.FraudCheckStatus.OK,
    ).first()
