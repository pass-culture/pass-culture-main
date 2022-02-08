import logging

from sqlalchemy import Integer
from sqlalchemy.orm import load_only

from pcapi.core.fraud import models as fraud_models
from pcapi.models.beneficiary_import import BeneficiaryImport
from pcapi.models.beneficiary_import import BeneficiaryImportStatus
from pcapi.models.beneficiary_import_status import ImportStatus


logger = logging.getLogger(__name__)


# TODO: get_already_processed_applications_ids_from_beneficiary_imports is temporary.
#       It should be removed when all the current imports are done.
#       Check: 08/03/2022 @lixxday or #skwadak in slack
def get_already_processed_applications_ids(procedure_id: int) -> set[int]:
    return get_already_processed_applications_ids_from_beneficiary_imports(
        procedure_id
    ) | get_already_processed_applications_ids_from_fraud_checks(procedure_id)


def get_already_processed_applications_ids_from_beneficiary_imports(procedure_id: int) -> set[int]:
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


def get_already_processed_applications_ids_from_fraud_checks(procedure_id: int) -> set[int]:
    fraud_check_queryset = fraud_models.BeneficiaryFraudCheck.query.filter(
        fraud_models.BeneficiaryFraudCheck.type == fraud_models.FraudCheckType.DMS,
        fraud_models.BeneficiaryFraudCheck.resultContent["procedure_id"].astext.cast(Integer) == procedure_id,
        fraud_models.BeneficiaryFraudCheck.status.notin_(
            [
                fraud_models.FraudCheckStatus.PENDING,
                fraud_models.FraudCheckStatus.STARTED,
            ]
        ),
    )
    fraud_check_ids = {
        int(fraud_check[0])
        for fraud_check in fraud_check_queryset.with_entities(fraud_models.BeneficiaryFraudCheck.thirdPartyId)
    }
    orphans_queryset = fraud_models.OrphanDmsApplication.query.filter(
        fraud_models.OrphanDmsApplication.process_id == procedure_id
    )
    orphans_ids = {
        orphan[0] for orphan in orphans_queryset.with_entities(fraud_models.OrphanDmsApplication.application_id)
    }

    return fraud_check_ids | orphans_ids
