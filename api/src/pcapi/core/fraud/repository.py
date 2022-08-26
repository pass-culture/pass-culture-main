from pcapi.core.users import models as users_models
from pcapi.models import db

from . import models


def get_last_user_profiling_fraud_check(user: users_models.User) -> models.BeneficiaryFraudCheck | None:
    # User profiling is not performed for UNDERAGE credit, no need to filter on eligibilityType here
    return (
        models.BeneficiaryFraudCheck.query.filter(
            models.BeneficiaryFraudCheck.user == user,
            models.BeneficiaryFraudCheck.type == models.FraudCheckType.USER_PROFILING,
        )
        .order_by(models.BeneficiaryFraudCheck.dateCreated.desc())
        .first()
    )


def has_failed_phone_validation(user: users_models.User) -> bool:
    return db.session.query(
        models.BeneficiaryFraudCheck.query.filter(
            models.BeneficiaryFraudCheck.userId == user.id,
            models.BeneficiaryFraudCheck.status == models.FraudCheckStatus.KO,
            models.BeneficiaryFraudCheck.type == models.FraudCheckType.PHONE_VALIDATION,
        ).exists()
    ).scalar()
