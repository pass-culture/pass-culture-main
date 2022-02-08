from typing import Optional

from pcapi.core.users import models as users_models
from pcapi.models import db

from . import models


def get_last_user_profiling_fraud_check(user: users_models.User) -> Optional[models.BeneficiaryFraudCheck]:
    # User profiling is not performed for UNDERAGE credit, no need to filter on eligibilityType here
    return (
        models.BeneficiaryFraudCheck.query.filter(
            models.BeneficiaryFraudCheck.user == user,
            models.BeneficiaryFraudCheck.type == models.FraudCheckType.USER_PROFILING,
        )
        .order_by(models.BeneficiaryFraudCheck.dateCreated.desc())
        .first()
    )


def get_identity_fraud_checks(
    user: users_models.User, eligibilityType: users_models.EligibilityType
) -> list[models.BeneficiaryFraudCheck]:
    return models.BeneficiaryFraudCheck.query.filter(
        models.BeneficiaryFraudCheck.user == user,
        models.BeneficiaryFraudCheck.type.in_(models.IDENTITY_CHECK_TYPES),
        models.BeneficiaryFraudCheck.eligibilityType == eligibilityType,
    ).all()


def has_failed_phone_validation(user) -> bool:
    return db.session.query(
        models.BeneficiaryFraudCheck.query.filter(
            models.BeneficiaryFraudCheck.userId == user.id,
            models.BeneficiaryFraudCheck.status == models.FraudCheckStatus.KO,
            models.BeneficiaryFraudCheck.type == models.FraudCheckType.PHONE_VALIDATION,
        ).exists()
    ).scalar()


def create_orphan_dms_application(
    application_id: int, procedure_id: int, email: str = ""
) -> models.OrphanDmsApplication:
    orphan_dms_application = models.OrphanDmsApplication(
        application_id=application_id, process_id=procedure_id, email=email
    )
    db.session.add(orphan_dms_application)
    db.session.commit()
    return orphan_dms_application
