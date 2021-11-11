from typing import Optional

from pcapi.core.users import models as users_models
from pcapi.models import BeneficiaryImport
from pcapi.models import BeneficiaryImportStatus
from pcapi.models import ImportStatus


def get_beneficiary_import_for_beneficiary(user: users_models.User) -> Optional[BeneficiaryImport]:
    return (
        BeneficiaryImport.query.join(BeneficiaryImportStatus)
        .filter(BeneficiaryImportStatus.status == ImportStatus.CREATED)
        .filter(BeneficiaryImport.beneficiaryId == user.id)
        .order_by(BeneficiaryImportStatus.date.desc())
        .first()
    )
