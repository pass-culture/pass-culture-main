from sqlalchemy import asc
from sqlalchemy.orm import load_only

from pcapi.core.users.models import User
from pcapi.models import BeneficiaryImport
from pcapi.models import BeneficiaryImportSources
from pcapi.models import BeneficiaryImportStatus
from pcapi.models import ImportStatus
from pcapi.models.db import db
from pcapi.repository import repository


def is_already_imported(application_id: int) -> bool:
    # FIXME (dbaty, 2021-04-22): `BeneficiaryImport.applicationId` is
    # not unique, we should probably look for a `(applicationId,  sourceId)`
    # pair (which is unique).
    beneficiary_import = (
        BeneficiaryImport.query.join(BeneficiaryImportStatus)
        .filter(BeneficiaryImport.applicationId == application_id)
        .filter(
            BeneficiaryImportStatus.status.in_(
                [ImportStatus.CREATED, ImportStatus.REJECTED, ImportStatus.DUPLICATE, ImportStatus.ERROR]
            )
        )
        .first()
    )
    return beneficiary_import is not None


def get_existing_applications_id(procedure_id: int) -> set[int]:
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
    detail: str = None,
    user: User = None,
) -> BeneficiaryImport:
    # FIXME (dbaty, 2021-04-22): see comment above about the non-uniqueness of application_id
    existing_beneficiary_import = BeneficiaryImport.query.filter_by(applicationId=application_id).first()

    beneficiary_import = existing_beneficiary_import or BeneficiaryImport()
    if not beneficiary_import.beneficiary:
        beneficiary_import.beneficiary = user

    beneficiary_import.applicationId = application_id
    beneficiary_import.sourceId = source_id
    beneficiary_import.source = source.value
    beneficiary_import.setStatus(status=status, detail=detail, author=None)

    repository.save(beneficiary_import)

    return beneficiary_import


def find_applications_ids_to_retry() -> list[int]:
    ids = (
        db.session.query(BeneficiaryImport.applicationId)
        .filter(BeneficiaryImport.currentStatus == ImportStatus.RETRY)
        .order_by(asc(BeneficiaryImport.applicationId))
        .all()
    )

    return sorted(list(map(lambda result_set: result_set[0], ids)))
