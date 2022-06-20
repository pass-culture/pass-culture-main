"""
Sometimes the ubble webhook does not reach our API. This is a problem because the application is still pending.
We want to be able to retrieve the processed applications and update the status of the application anyway.
"""

import datetime
import logging

from pcapi.core.fraud import models as fraud_models
from pcapi.core.subscription.ubble import api as ubble_api
from pcapi.models import db


logger = logging.getLogger(__name__)


def update_pending_ubble_applications(dry_run: bool = True) -> None:
    # Ubble guaranties an application is processed after 3 hours.
    # We give ourselves some extra time and we retrieve the applications that are still pending after 12 hours.
    TWELVE_HOURS_AGO = datetime.date.today() - datetime.timedelta(hours=12)
    pending_ubble_application_fraud_checks = fraud_models.BeneficiaryFraudCheck.query.filter(
        fraud_models.BeneficiaryFraudCheck.type == fraud_models.FraudCheckType.UBBLE,
        fraud_models.BeneficiaryFraudCheck.status == fraud_models.FraudCheckStatus.PENDING,
        fraud_models.BeneficiaryFraudCheck.dateCreated < TWELVE_HOURS_AGO,
    ).all()
    if len(pending_ubble_application_fraud_checks) > 0:
        logger.warning(
            "Found %d pending ubble application older than 12 hours. Updating them.",
            len(pending_ubble_application_fraud_checks),
        )
    else:
        logger.info("No pending ubble application found older than 12 hours. This is good.")
    for fraud_check in pending_ubble_application_fraud_checks:
        try:
            ubble_api.update_ubble_workflow(fraud_check)
        except Exception:  # pylint: disable=broad-except
            logger.error(
                "Error while updating pending ubble application",
                extra={"fraud_check_id": fraud_check.id, "ubble_id": fraud_check.thirdPartyId},
            )
            continue
        db.session.refresh(fraud_check)
        if fraud_check.status == fraud_models.FraudCheckStatus.PENDING:
            logger.error(
                "Pending ubble application still pending after 12 hours. This is a problem.",
                extra={"fraud_check_id": fraud_check.id, "ubble_id": fraud_check.thirdPartyId},
            )
