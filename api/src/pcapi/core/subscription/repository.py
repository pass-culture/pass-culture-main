from typing import Optional

from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.models.beneficiary_import import BeneficiaryImport
from pcapi.models.beneficiary_import_status import BeneficiaryImportStatus
from pcapi.models.beneficiary_import_status import ImportStatus


def get_beneficiary_import_for_beneficiary(user: users_models.User) -> Optional[BeneficiaryImport]:
    return (
        BeneficiaryImport.query.join(BeneficiaryImportStatus)
        .filter(BeneficiaryImportStatus.status == ImportStatus.CREATED)
        .filter(BeneficiaryImport.beneficiaryId == user.id)
        .order_by(BeneficiaryImportStatus.date.desc())
        .first()
    )


def has_created_beneficiary_import_of_eligibility(
    user: users_models.User, eligibility: users_models.EligibilityType
) -> bool:
    return db.session.query(
        BeneficiaryImport.query.join(BeneficiaryImportStatus)
        .filter(BeneficiaryImport.beneficiaryId == user.id)
        .filter(BeneficiaryImport.eligibilityType == eligibility)
        .filter(BeneficiaryImportStatus.status == ImportStatus.CREATED)
        .exists()
    ).scalar()
