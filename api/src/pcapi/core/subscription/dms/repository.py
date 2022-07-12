from sqlalchemy import Integer
from sqlalchemy import or_

from pcapi.core.fraud import models as fraud_models
from pcapi.models import db


def create_orphan_dms_application_if_not_exists(
    application_number: int, procedure_number: int, email: str | None = None
) -> None:
    if db.session.query(
        fraud_models.OrphanDmsApplication.query.filter_by(application_id=application_number, email=email).exists()
    ).scalar():
        return

    orphan_dms_application = fraud_models.OrphanDmsApplication(
        application_id=application_number, process_id=procedure_number, email=email
    )
    db.session.add(orphan_dms_application)
    db.session.commit()


def get_already_processed_applications_ids(procedure_number: int) -> set[int]:
    return _get_already_processed_applications_ids_from_orphans(
        procedure_number
    ) | _get_already_processed_applications_ids_from_fraud_checks(procedure_number)


def _get_already_processed_applications_ids_from_orphans(procedure_number: int) -> set[int]:
    orphans = (
        fraud_models.OrphanDmsApplication.query.filter(fraud_models.OrphanDmsApplication.process_id == procedure_number)
        .with_entities(fraud_models.OrphanDmsApplication.application_id)
        .all()
    )

    return {orphan[0] for orphan in orphans}


def _get_already_processed_applications_ids_from_fraud_checks(procedure_number: int) -> set[int]:
    fraud_checks = fraud_models.BeneficiaryFraudCheck.query.filter(
        fraud_models.BeneficiaryFraudCheck.type == fraud_models.FraudCheckType.DMS,
        or_(
            fraud_models.BeneficiaryFraudCheck.resultContent
            == None,  # If there was a parsing error, a fraudCheck exists but no resultContent
            fraud_models.BeneficiaryFraudCheck.resultContent["procedure_id"].astext.cast(Integer) == procedure_number,
        ),
        fraud_models.BeneficiaryFraudCheck.status.notin_(
            [
                fraud_models.FraudCheckStatus.PENDING,
                fraud_models.FraudCheckStatus.STARTED,
            ]
        ),
    ).with_entities(fraud_models.BeneficiaryFraudCheck.thirdPartyId)

    return {int(fraud_check[0]) for fraud_check in fraud_checks}
