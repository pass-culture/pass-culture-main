from typing import Optional

from pcapi.core.users import models as users_models

from . import models


def get_current_beneficiary_fraud_result(
    user: users_models.User, eligibilityType: users_models.EligibilityType
) -> Optional[models.BeneficiaryFraudResult]:
    return models.BeneficiaryFraudResult.query.filter(
        models.BeneficiaryFraudResult.userId == user.id,
        models.BeneficiaryFraudResult.eligibilityType == eligibilityType,
    ).one_or_none()
