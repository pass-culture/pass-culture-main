import datetime
import logging
import typing

from sqlalchemy import Integer
from typing_extensions import TypeGuard

from pcapi.connectors.dms import api as dms_api
from pcapi.connectors.dms import models as dms_models
from pcapi.core.fraud import models as fraud_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def is_dms_content(obj: typing.Any) -> TypeGuard[fraud_models.DMSContent]:
    return isinstance(obj, fraud_models.DMSContent)


def get_latest_deleted_application_datetime(procedure_id: int) -> typing.Optional[datetime.datetime]:
    fraud_check: typing.Optional[fraud_models.BeneficiaryFraudCheck] = (
        fraud_models.BeneficiaryFraudCheck.query.filter(
            fraud_models.BeneficiaryFraudCheck.type == fraud_models.FraudCheckType.DMS,
            fraud_models.BeneficiaryFraudCheck.status == fraud_models.FraudCheckStatus.CANCELED,
            fraud_models.BeneficiaryFraudCheck.resultContent.isnot(None),
            fraud_models.BeneficiaryFraudCheck.resultContent["procedure_id"].astext.cast(Integer) == procedure_id,
            fraud_models.BeneficiaryFraudCheck.resultContent.has_key("deletion_datetime"),  # type: ignore [attr-defined]
        )
        .order_by(fraud_models.BeneficiaryFraudCheck.resultContent["deletion_datetime"].desc())
        .first()
    )
    if fraud_check:
        content = fraud_check.source_data()
        if is_dms_content(content):
            return content.deletion_datetime

        raise ValueError(f"fraud_check.source_data() is not a DMSContent. Fraud check: {fraud_check.id}")
    return None


def handle_deleted_dms_applications(procedure_id: int) -> None:
    latest_deleted_application_datetime = get_latest_deleted_application_datetime(procedure_id)

    logger.info(
        "Looking for deleted applications for procedure %d since %s", procedure_id, latest_deleted_application_datetime
    )

    dms_graphql_client = dms_api.DMSGraphQLClient()
    applications_to_mark_as_deleted = {}

    for deleted_application in dms_graphql_client.get_deleted_applications(
        procedure_id, deletedSince=latest_deleted_application_datetime
    ):
        applications_to_mark_as_deleted[str(deleted_application.number)] = deleted_application

    fraud_checks_to_mark_as_deleted = fraud_models.BeneficiaryFraudCheck.query.filter(
        fraud_models.BeneficiaryFraudCheck.thirdPartyId.in_(applications_to_mark_as_deleted),
        fraud_models.BeneficiaryFraudCheck.type == fraud_models.FraudCheckType.DMS,
        fraud_models.BeneficiaryFraudCheck.status != fraud_models.FraudCheckStatus.CANCELED,
    ).yield_per(100)
    updated_fraud_checks_count = 0

    for fraud_check in fraud_checks_to_mark_as_deleted:
        dms_information: dms_models.DmsDeletedApplication = applications_to_mark_as_deleted[fraud_check.thirdPartyId]
        try:
            fraud_check_data: fraud_models.DMSContent = fraud_check.source_data()
            fraud_check_data.deletion_datetime = dms_information.deletion_datetime
            fraud_check.resultContent = fraud_check_data
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
        procedure_id,
        latest_deleted_application_datetime,
    )
