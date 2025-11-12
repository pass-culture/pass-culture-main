import logging

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
