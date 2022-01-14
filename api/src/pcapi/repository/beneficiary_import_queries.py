from typing import Optional

from sqlalchemy.orm import load_only

from pcapi.core.users import models as users_models
from pcapi.models.beneficiary_import import BeneficiaryImport
from pcapi.models.beneficiary_import import BeneficiaryImportSources
from pcapi.models.beneficiary_import_status import BeneficiaryImportStatus
from pcapi.models.beneficiary_import_status import ImportStatus
from pcapi.repository import repository


def get_already_processed_applications_ids(procedure_id: int) -> set[int]:
    return {
        beneficiary_import.applicationId
        for beneficiary_import in BeneficiaryImport.query.join(BeneficiaryImportStatus)
        .filter(
            BeneficiaryImportStatus.status.in_(
                [ImportStatus.CREATED, ImportStatus.REJECTED, ImportStatus.DUPLICATE, ImportStatus.ERROR]
            )
        )
        .options(load_only(BeneficiaryImport.applicationId))
        .filter(BeneficiaryImport.sourceId == procedure_id)
        .all()
    }


def save_beneficiary_import_with_status(
    status: ImportStatus,
    application_id: int,
    source_id: int,
    source: BeneficiaryImportSources,
    eligibility_type: Optional[users_models.EligibilityType],
    detail: str = None,
    user: users_models.User = None,
) -> BeneficiaryImport:
    # FIXME (dbaty, 2021-04-22): see comment above about the non-uniqueness of application_id
    existing_beneficiary_import = BeneficiaryImport.query.filter_by(applicationId=application_id).first()

    beneficiary_import = existing_beneficiary_import or BeneficiaryImport()
    if not beneficiary_import.beneficiary:
        beneficiary_import.beneficiary = user

    beneficiary_import.applicationId = application_id
    beneficiary_import.sourceId = source_id
    beneficiary_import.source = source.value

    if eligibility_type is not None:
        beneficiary_import.eligibilityType = eligibility_type
    beneficiary_import.setStatus(status=status, detail=detail, author=None)

    repository.save(beneficiary_import)

    return beneficiary_import
