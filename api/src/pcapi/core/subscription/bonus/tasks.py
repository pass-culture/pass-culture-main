import datetime
import logging

import sqlalchemy as sa
from dateutil.relativedelta import relativedelta
from pydantic import BaseModel as BaseModelV2

from pcapi import settings
from pcapi.celery_tasks.tasks import celery_async_task
from pcapi.connectors import api_particulier
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription.bonus.api import apply_for_quotient_familial_bonus
from pcapi.models import db


logger = logging.getLogger(__name__)


# the task calls the quotient familial endpoint for each month of a year
QUOTIENT_FAMILIAL_TASK_RATE_LIMIT = settings.PARTICULIER_API_RATE_LIMIT_THRESHOLD // 12


class GetQuotientFamilialTaskPayload(BaseModelV2):
    fraud_check_id: int


@celery_async_task(
    name="tasks.api_particulier.default.get_quotient_familial",
    model=GetQuotientFamilialTaskPayload,
    autoretry_for=(api_particulier.ParticulierApiUnavailable, api_particulier.ParticulierApiRateLimitExceeded),
    max_per_time_window=QUOTIENT_FAMILIAL_TASK_RATE_LIMIT,
    time_window_size=settings.PARTICULIER_API_RATE_LIMIT_TIME_WINDOW_SECONDS,
)
def apply_for_quotient_familial_bonus_task(payload: GetQuotientFamilialTaskPayload) -> None:
    fraud_check = (
        db.session.query(subscription_models.BeneficiaryFraudCheck)
        .filter(
            subscription_models.BeneficiaryFraudCheck.id == payload.fraud_check_id,
        )
        .one()
    )
    if fraud_check.type != subscription_models.FraudCheckType.QF_BONUS_CREDIT:
        logger.error(
            "Trying to fetch FraudCheck #%s of type BONUS_CREDIT resulted in a FraudCheck of type %s",
            fraud_check.id,
            fraud_check.type,
        )
        return

    if fraud_check.status != subscription_models.FraudCheckStatus.STARTED:
        logger.warning("Trying to handle already processed bonus fraud check #%s", payload.fraud_check_id)
        return

    apply_for_quotient_familial_bonus(fraud_check)


def recover_started_quotient_familial_application() -> None:
    """
    Recovers the `page_size` first started Quotient Familial fraud checks.
    This function only recovers the first page, and is meant to be called as often as needed by recovery workers.
    """
    twelve_hours_ago = datetime.datetime.now(tz=None) - relativedelta(hours=12)
    started_qf_fraud_check_stmt = (
        sa.select(subscription_models.BeneficiaryFraudCheck.id)
        .filter(
            subscription_models.BeneficiaryFraudCheck.type == subscription_models.FraudCheckType.QF_BONUS_CREDIT,
            subscription_models.BeneficiaryFraudCheck.status == subscription_models.FraudCheckStatus.STARTED,
            subscription_models.BeneficiaryFraudCheck.updatedAt <= twelve_hours_ago,
        )
        .order_by(subscription_models.BeneficiaryFraudCheck.id)
        .limit(QUOTIENT_FAMILIAL_TASK_RATE_LIMIT)
    )
    started_qf_fraud_check_ids = db.session.scalars(started_qf_fraud_check_stmt).all()

    for fraud_check_id in started_qf_fraud_check_ids:
        payload = GetQuotientFamilialTaskPayload(fraud_check_id=fraud_check_id)
        apply_for_quotient_familial_bonus_task.delay(payload=payload.model_dump())
