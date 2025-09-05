import datetime
import logging

import sqlalchemy as sa

from pcapi import settings
from pcapi.connectors.dms import api as dms_api
from pcapi.connectors.dms import models as dms_models
from pcapi.core.fraud import models as fraud_models
from pcapi.models import db


logger = logging.getLogger()


def get_orphan_dms_application_by_application_id(application_id: int) -> fraud_models.OrphanDmsApplication | None:
    return db.session.query(fraud_models.OrphanDmsApplication).filter_by(application_id=application_id).first()


def create_orphan_dms_application(
    application_number: int,
    procedure_number: int,
    latest_modification_datetime: datetime.datetime,
    email: str | None = None,
) -> None:
    orphan_dms_application = fraud_models.OrphanDmsApplication(
        application_id=application_number,
        process_id=procedure_number,
        email=email,
        latest_modification_datetime=latest_modification_datetime,
    )
    db.session.add(orphan_dms_application)
    db.session.commit()


def _get_already_processed_applications_ids(procedure_number: int) -> set[int]:
    return _get_already_processed_applications_ids_from_orphans(
        procedure_number
    ) | _get_already_processed_applications_ids_from_fraud_checks(procedure_number)


def _get_already_processed_applications_ids_from_orphans(procedure_number: int) -> set[int]:
    orphans = (
        db.session.query(fraud_models.OrphanDmsApplication)
        .filter(fraud_models.OrphanDmsApplication.process_id == procedure_number)
        .with_entities(fraud_models.OrphanDmsApplication.application_id)
        .all()
    )

    return {orphan[0] for orphan in orphans}


def _get_already_processed_applications_ids_from_fraud_checks(procedure_number: int) -> set[int]:
    fraud_checks = (
        db.session.query(fraud_models.BeneficiaryFraudCheck)
        .filter(
            fraud_models.BeneficiaryFraudCheck.type == fraud_models.FraudCheckType.DMS,
            sa.or_(
                # If there was a parsing error, a fraudCheck exists but no resultContent
                fraud_models.BeneficiaryFraudCheck.resultContent.is_(None),
                fraud_models.BeneficiaryFraudCheck.resultContent["procedure_id"].astext.cast(sa.Integer)
                == procedure_number,
            ),
            fraud_models.BeneficiaryFraudCheck.status.notin_(
                [
                    fraud_models.FraudCheckStatus.PENDING,
                    fraud_models.FraudCheckStatus.STARTED,
                ]
            ),
        )
        .with_entities(fraud_models.BeneficiaryFraudCheck.thirdPartyId)
    )

    return {int(fraud_check[0]) for fraud_check in fraud_checks}


def archive_applications(procedure_number: int, dry_run: bool = True) -> None:
    total_applications = 0
    archived_applications = 0

    already_processed_applications_ids = _get_already_processed_applications_ids(procedure_number)
    client = dms_api.DMSGraphQLClient()

    for application_details in client.get_applications_with_details(
        procedure_number, dms_models.GraphQLApplicationStates.accepted
    ):
        total_applications += 1

        application_techid = application_details.id
        application_number = application_details.number

        if application_number not in already_processed_applications_ids:
            continue

        if not dry_run:
            try:
                client.archive_application(application_techid, settings.DMS_ENROLLMENT_INSTRUCTOR)
            except Exception:
                logger.exception("error while archiving application %d", application_number)
        logger.info("Archiving application %d on procedure %d", application_number, procedure_number)
        archived_applications += 1

    logger.info(
        "script ran : total applications : %d to archive applications : %d", total_applications, archived_applications
    )


def _get_latest_deleted_application_datetime(procedure_number: int) -> datetime.datetime | None:
    fraud_check: fraud_models.BeneficiaryFraudCheck | None = (
        db.session.query(fraud_models.BeneficiaryFraudCheck)
        .filter(
            fraud_models.BeneficiaryFraudCheck.type == fraud_models.FraudCheckType.DMS,
            fraud_models.BeneficiaryFraudCheck.status == fraud_models.FraudCheckStatus.CANCELED,
            fraud_models.BeneficiaryFraudCheck.resultContent.is_not(None),
            fraud_models.BeneficiaryFraudCheck.resultContent["procedure_id"].astext.cast(sa.Integer)
            == procedure_number,
            fraud_models.BeneficiaryFraudCheck.resultContent.has_key("deletion_datetime"),
        )
        .order_by(fraud_models.BeneficiaryFraudCheck.resultContent["deletion_datetime"].desc())
        .first()
    )
    if fraud_check:
        content = fraud_check.source_data()
        if isinstance(content, fraud_models.DMSContent):
            return content.deletion_datetime

        raise ValueError(f"fraud_check.source_data() is not a DMSContent. Fraud check: {fraud_check.id}")
    return None


def handle_deleted_dms_applications(procedure_number: int) -> None:
    latest_deleted_application_datetime = _get_latest_deleted_application_datetime(procedure_number)

    logger.info(
        "Looking for deleted applications for procedure %d since %s",
        procedure_number,
        latest_deleted_application_datetime,
    )

    dms_graphql_client = dms_api.DMSGraphQLClient()
    applications_to_mark_as_deleted = {}

    for deleted_application in dms_graphql_client.get_deleted_applications(
        procedure_number, deletedSince=latest_deleted_application_datetime
    ):
        applications_to_mark_as_deleted[str(deleted_application.number)] = deleted_application

    fraud_checks_to_mark_as_deleted = (
        db.session.query(fraud_models.BeneficiaryFraudCheck)
        .filter(
            fraud_models.BeneficiaryFraudCheck.thirdPartyId.in_(applications_to_mark_as_deleted),
            fraud_models.BeneficiaryFraudCheck.type == fraud_models.FraudCheckType.DMS,
            fraud_models.BeneficiaryFraudCheck.status != fraud_models.FraudCheckStatus.CANCELED,
            fraud_models.BeneficiaryFraudCheck.status != fraud_models.FraudCheckStatus.OK,
        )
        .yield_per(100)
    )
    updated_fraud_checks_count = 0

    for fraud_check in fraud_checks_to_mark_as_deleted:
        dms_information: dms_models.DmsDeletedApplication = applications_to_mark_as_deleted[fraud_check.thirdPartyId]
        try:
            fraud_check_data: fraud_models.DMSContent = fraud_check.source_data()
            fraud_check_data.deletion_datetime = dms_information.deletion_datetime
            fraud_check.resultContent = fraud_check_data.dict()
        except ValueError:
            logger.warning(
                "Could not write 'deletion_datetime' in fraud check resultContent: resultContent is empty",
                extra={"fraud_check": fraud_check.id, "deletion_datetime": dms_information.deletion_datetime},
            )

        fraud_check.status = fraud_models.FraudCheckStatus.CANCELED
        fraud_check.reason = f"Dossier supprimé sur démarches-simplifiées. Motif: {dms_information.reason}"

        db.session.add(fraud_check)
        updated_fraud_checks_count += 1
    db.session.commit()

    logger.info(
        "Marked %d fraud checks as deleted for procedure %d since %s",
        updated_fraud_checks_count,
        procedure_number,
        latest_deleted_application_datetime,
    )
