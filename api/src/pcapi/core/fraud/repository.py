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


def get_last_user_profiling_fraud_check(user: users_models.User) -> Optional[models.BeneficiaryFraudCheck]:
    return (
        models.BeneficiaryFraudCheck.query.filter(models.BeneficiaryFraudCheck.user == user)
        .filter(models.BeneficiaryFraudCheck.type == models.FraudCheckType.USER_PROFILING)
        .order_by(models.BeneficiaryFraudCheck.dateCreated.desc())
        .first()
    )
