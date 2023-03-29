from pcapi.core.fraud import models as fraud_models
from pcapi.core.users import models as users_models


def get_completed_profile_check(
    user: users_models.User, eligibility: users_models.EligibilityType | None
) -> fraud_models.BeneficiaryFraudCheck | None:
    # user.beneficiaryFraudChecks should have been joinedloaded before to reduce the number of db requests
    profile_completion_checks = [
        fraud_check
        for fraud_check in user.beneficiaryFraudChecks
        if fraud_check.type == fraud_models.FraudCheckType.PROFILE_COMPLETION
        and fraud_check.eligibilityType == eligibility
        and fraud_check.status == fraud_models.FraudCheckStatus.OK
    ]

    if profile_completion_checks:
        return profile_completion_checks[0]

    return None
