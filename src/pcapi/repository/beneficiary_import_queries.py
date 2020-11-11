from typing import List

from sqlalchemy import asc

from pcapi.models import BeneficiaryImport
from pcapi.models import BeneficiaryImportSources
from pcapi.models import ImportStatus
from pcapi.models import UserSQLEntity
from pcapi.models.db import db
from pcapi.repository import repository


def is_already_imported(application_id: int) -> bool:
    beneficiary_import = BeneficiaryImport.query.filter(BeneficiaryImport.applicationId == application_id).first()

    if beneficiary_import is None:
        return False

    return beneficiary_import.currentStatus != ImportStatus.RETRY


def save_beneficiary_import_with_status(
    status: ImportStatus,
    application_id: int,
    source_id: int,
    source: BeneficiaryImportSources,
    detail: str = None,
    user: UserSQLEntity = None,
) -> None:
    existing_beneficiary_import = BeneficiaryImport.query.filter_by(applicationId=application_id).first()

    beneficiary_import = existing_beneficiary_import or BeneficiaryImport()
    if not beneficiary_import.beneficiary:
        beneficiary_import.beneficiary = user

    beneficiary_import.applicationId = application_id
    beneficiary_import.sourceId = source_id
    beneficiary_import.source = source.value
    beneficiary_import.setStatus(status=status, detail=detail, author=None)

    repository.save(beneficiary_import)


def find_applications_ids_to_retry() -> List[int]:
    ids = (
        db.session.query(BeneficiaryImport.applicationId)
        .filter(BeneficiaryImport.currentStatus == ImportStatus.RETRY)
        .order_by(asc(BeneficiaryImport.applicationId))
        .all()
    )

    return sorted(list(map(lambda result_set: result_set[0], ids)))
