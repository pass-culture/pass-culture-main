import logging
import typing

from pydantic import BaseModel as BaseModelV2

from pcapi import settings
from pcapi.celery_tasks.tasks import celery_async_task
from pcapi.connectors import api_particulier as api
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription.bonus.schemas import BonusCreditContent
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic


logger = logging.getLogger(__name__)


class GetQuotientFamilialTaskPayload(BaseModelV2):
    fraud_check_id: int


@celery_async_task(
    name="tasks.api_particulier.default.get_quotient_familial",
    model=GetQuotientFamilialTaskPayload,
    autoretry_for=(api.ParticulierApiUnavailable, api.ParticulierApiRateLimitExceeded),
    max_per_time_window=settings.PARTICULIER_API_RATE_LIMIT_THRESHOLD,
    time_window_size=settings.PARTICULIER_API_RATE_LIMIT_TIME_WINDOW_SECONDS,
)
def get_quotient_familial_task(payload: GetQuotientFamilialTaskPayload) -> None:
    fraud_check = (
        db.session.query(subscription_models.BeneficiaryFraudCheck)
        .filter(
            subscription_models.BeneficiaryFraudCheck.id == payload.fraud_check_id,
        )
        .one()
    )
    if fraud_check.type != subscription_models.FraudCheckType.BONUS_CREDIT:
        logger.error(
            "Trying to fetch FraudCheck #%s of type BONUS_CREDIT resulted in a FraudCheck of type %s",
            fraud_check.id,
            fraud_check.type,
        )
        return

    if fraud_check.status != subscription_models.FraudCheckStatus.STARTED:
        logger.warning("Trying to handle already processed bonus fraud check #%s", payload.fraud_check_id)
        return
    source_data: BonusCreditContent = typing.cast(BonusCreditContent, fraud_check.source_data())
    logger.info("Fetching quotient familial from fraud check #%s", payload.fraud_check_id)

    api.get_quotient_familial(
        last_name=source_data.custodian.last_name,
        first_names=source_data.custodian.first_names,
        birth_date=source_data.custodian.birth_date,
        gender=source_data.custodian.gender,
        country_insee_code=source_data.custodian.birth_country_cog_code,
        city_insee_code=source_data.custodian.birth_city_cog_code,
        quotient_familial_date=fraud_check.dateCreated.date(),
    )
    with atomic():
        # TODO: Store the value of `response.data.quotient_familial` inside the "atomic" bloc
        fraud_check.status = subscription_models.FraudCheckStatus.OK
        db.session.add(fraud_check)
