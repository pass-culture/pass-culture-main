import datetime
import logging

import sqlalchemy as sa

from pcapi.core.subscription import models as subscription_models
from pcapi.models import db


logger = logging.getLogger()


def get_orphan_dms_application_by_application_id(
    application_id: int,
) -> subscription_models.OrphanDmsApplication | None:
    return db.session.query(subscription_models.OrphanDmsApplication).filter_by(application_id=application_id).first()


def create_orphan_dms_application(
    application_number: int,
    procedure_number: int,
    latest_modification_datetime: datetime.datetime,
    email: str | None = None,
) -> None:
    orphan_dms_application = subscription_models.OrphanDmsApplication(
        application_id=application_number,
        process_id=procedure_number,
        email=email,
        latest_modification_datetime=latest_modification_datetime,
    )
    db.session.add(orphan_dms_application)
    db.session.commit()


def get_already_processed_applications_ids(procedure_number: int) -> set[int]:
    return _get_already_processed_applications_ids_from_orphans(
        procedure_number
    ) | _get_already_processed_applications_ids_from_fraud_checks(procedure_number)


def _get_already_processed_applications_ids_from_orphans(procedure_number: int) -> set[int]:
    orphans = (
        db.session.query(subscription_models.OrphanDmsApplication)
        .filter(subscription_models.OrphanDmsApplication.process_id == procedure_number)
        .with_entities(subscription_models.OrphanDmsApplication.application_id)
        .all()
    )

    return {orphan[0] for orphan in orphans}


def _get_already_processed_applications_ids_from_fraud_checks(procedure_number: int) -> set[int]:
    fraud_checks = (
        db.session.query(subscription_models.BeneficiaryFraudCheck)
        .filter(
            subscription_models.BeneficiaryFraudCheck.type == subscription_models.FraudCheckType.DMS,
            sa.or_(
                # If there was a parsing error, a fraudCheck exists but no resultContent
                subscription_models.BeneficiaryFraudCheck.resultContent.is_(None),
                subscription_models.BeneficiaryFraudCheck.resultContent["procedure_id"].astext.cast(sa.Integer)
                == procedure_number,
            ),
            subscription_models.BeneficiaryFraudCheck.status.notin_(
                [
                    subscription_models.FraudCheckStatus.PENDING,
                    subscription_models.FraudCheckStatus.STARTED,
                ]
            ),
        )
        .with_entities(subscription_models.BeneficiaryFraudCheck.thirdPartyId)
    )

    return {int(fraud_check[0]) for fraud_check in fraud_checks}
