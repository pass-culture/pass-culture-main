"""
Sometimes the ubble webhook does not reach our API. This is a problem because the application is still pending.
We want to be able to retrieve the processed applications and update the status of the application anyway.
"""

import datetime
import logging
import typing

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

from pcapi.core.finance import models as finance_models
from pcapi.core.fraud import models as fraud_models
from pcapi.core.subscription.ubble import api as ubble_api
from pcapi.core.users import models as users_models
from pcapi.models import db


logger = logging.getLogger(__name__)

PAGE_SIZE = 200_000


def update_pending_ubble_applications(dry_run: bool = True) -> None:
    pending_ubble_application_counter = 0
    for pending_ubble_application_fraud_checks in _get_pending_fraud_checks_pages():
        pending_ubble_application_counter += len(pending_ubble_application_fraud_checks)
        for fraud_check in pending_ubble_application_fraud_checks:
            try:
                ubble_api.update_ubble_workflow(fraud_check)
            except Exception:
                logger.error(
                    "Error while updating pending ubble application",
                    extra={"fraud_check_id": fraud_check.id, "ubble_id": fraud_check.thirdPartyId},
                )
                continue
            db.session.refresh(fraud_check)
            if fraud_check.status == fraud_models.FraudCheckStatus.PENDING:
                logger.error(
                    "Pending ubble application still pending after 12 hours. This is a problem on the Ubble side.",
                    extra={"fraud_check_id": fraud_check.id, "ubble_id": fraud_check.thirdPartyId},
                )

    if pending_ubble_application_counter > 0:
        logger.warning(
            "Found %d pending ubble application older than 12 hours and tried to update them.",
            pending_ubble_application_counter,
        )
    else:
        logger.info("No pending ubble application found older than 12 hours. This is good.")


def _get_pending_fraud_checks_pages() -> typing.Generator[list[fraud_models.BeneficiaryFraudCheck], None, None]:
    # Ubble guarantees an application is processed after 3 hours.
    # We give ourselves some extra time and we retrieve the applications that are still pending after 12 hours.
    twelve_hours_ago = datetime.date.today() - datetime.timedelta(hours=12)
    last_fraud_check_id = 0
    max_ubble_fraud_check_id = (
        db.session.query(sa.func.max(fraud_models.BeneficiaryFraudCheck.id))
        .filter(
            fraud_models.BeneficiaryFraudCheck.type == fraud_models.FraudCheckType.UBBLE,
            fraud_models.BeneficiaryFraudCheck.dateCreated < twelve_hours_ago,
        )
        .scalar()
    )

    pending_fraud_check_query = (
        db.session.query(fraud_models.BeneficiaryFraudCheck)
        .filter(
            fraud_models.BeneficiaryFraudCheck.type == fraud_models.FraudCheckType.UBBLE,
            fraud_models.BeneficiaryFraudCheck.status.in_(
                [fraud_models.FraudCheckStatus.STARTED, fraud_models.FraudCheckStatus.PENDING]
            ),
        )
        .options(
            sa_orm.joinedload(fraud_models.BeneficiaryFraudCheck.user)
            .selectinload(users_models.User.deposits)
            .selectinload(finance_models.Deposit.recredits)
        )
    )

    has_next_page = True
    while has_next_page:
        upper_fraud_check_page_id = last_fraud_check_id + PAGE_SIZE
        pending_fraud_check_page = pending_fraud_check_query.filter(
            fraud_models.BeneficiaryFraudCheck.id >= last_fraud_check_id,
            fraud_models.BeneficiaryFraudCheck.id < upper_fraud_check_page_id,
        ).all()

        yield pending_fraud_check_page

        has_next_page = upper_fraud_check_page_id <= max_ubble_fraud_check_id
        last_fraud_check_id = upper_fraud_check_page_id
