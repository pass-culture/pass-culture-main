import datetime
import logging

import sqlalchemy as sa

from pcapi import settings
from pcapi.celery_tasks.tasks import celery_async_task
from pcapi.connectors.beneficiaries import ubble as ubble_connector
from pcapi.core.finance import models as finance_models
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription.ubble import api as ubble_api
from pcapi.core.subscription.ubble import exceptions as ubble_exceptions
from pcapi.core.subscription.ubble import schemas as ubble_schemas
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic


logger = logging.getLogger(__name__)

# always leave some bandwidth for manual Ubble call through native app
UBBLE_TASK_RATE_LIMIT = int(settings.UBBLE_RATE_LIMIT * 0.9)


@celery_async_task(
    name="tasks.ubble.priority.update_ubble_workflow",
    model=ubble_schemas.UpdateWorkflowPayload,
    autoretry_for=(ubble_connector.UbbleRateLimitedError, ubble_connector.UbbleServerError),
    max_per_time_window=UBBLE_TASK_RATE_LIMIT,
    time_window_size=settings.UBBLE_TIME_WINDOW_SIZE,
)
def update_ubble_workflow_task(payload: ubble_schemas.UpdateWorkflowPayload) -> None:
    fraud_check_stmt = (
        sa.select(subscription_models.BeneficiaryFraudCheck)
        .where(subscription_models.BeneficiaryFraudCheck.id == payload.beneficiary_fraud_check_id)
        .options(
            sa.orm.joinedload(subscription_models.BeneficiaryFraudCheck.user)
            .selectinload(users_models.User.deposits)
            .selectinload(finance_models.Deposit.recredits)
        )
    )
    fraud_check = db.session.scalars(fraud_check_stmt).one()

    with atomic():
        ubble_api.update_ubble_workflow(fraud_check)

    if fraud_check.status == subscription_models.FraudCheckStatus.PENDING:
        logger.error(
            "Pending ubble application still pending after 12 hours. This is a problem on the Ubble side.",
            extra={"fraud_check_id": fraud_check.id, "ubble_id": fraud_check.thirdPartyId},
        )

    if fraud_check.status == subscription_models.FraudCheckStatus.STARTED:
        logger.error(
            "Started ubble application still started after 12 hours. This is a problem on our side.",
            extra={"fraud_check_id": fraud_check.id, "ubble_id": fraud_check.thirdPartyId},
        )


def update_ubble_workflow_if_needed(
    fraud_check: subscription_models.BeneficiaryFraudCheck, status: ubble_schemas.UbbleIdentificationStatus
) -> None:
    """
    Checks if a Ubble network call is needed according to the status returned by the Ubble webhook.

    Ubble's rate limit of 200 requests/minute can be easily reached during peak hours through
    the native app causing an influx of webhook notifications, plus recovery scripts.
    """
    if status in ubble_api.PENDING_STATUSES:
        fraud_check.status = subscription_models.FraudCheckStatus.PENDING
        fraud_check.updatedAt = datetime.datetime.now(datetime.timezone.utc)
        return

    if status in ubble_api.CANCELED_STATUSES:
        fraud_check.status = subscription_models.FraudCheckStatus.CANCELED
        fraud_check.updatedAt = datetime.datetime.now(datetime.timezone.utc)
        return

    if status not in ubble_api.CONCLUSIVE_STATUSES:
        return

    payload = ubble_schemas.UpdateWorkflowPayload(beneficiary_fraud_check_id=fraud_check.id)
    update_ubble_workflow_task.delay(payload.model_dump())


@celery_async_task(
    name="tasks.ubble.default.store_id_picture",
    model=ubble_schemas.StoreIdPicturePayload,
    autoretry_for=(ubble_connector.UbbleRateLimitedError, ubble_connector.UbbleServerError),
    max_per_time_window=settings.UBBLE_RATE_LIMIT,
    time_window_size=settings.UBBLE_TIME_WINDOW_SIZE,
)
def store_id_pictures_task(payload: ubble_schemas.StoreIdPicturePayload) -> None:
    try:
        ubble_api.archive_ubble_user_id_pictures(payload.identification_id)
    except ubble_exceptions.UbbleDownloadedFileEmpty as exc:
        logger.warning("File to archive is empty", extra={"exc": exc})
