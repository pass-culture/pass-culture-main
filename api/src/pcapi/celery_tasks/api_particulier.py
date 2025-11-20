import logging
import typing

from pydantic import BaseModel as BaseModelV2

from pcapi import settings
from pcapi.celery_tasks.tasks import celery_async_task
from pcapi.connectors import api_particulier as api
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription.bonus.schemas import QuotientFamilialBonusCreditContent
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic


logger = logging.getLogger(__name__)


class GetQutientFamilialTaskPayload(BaseModelV2):
    fraud_check_id: int


@celery_async_task(
    name="tasks.api_particulier.default.get_quotient_familial",
    model=GetQutientFamilialTaskPayload,
    autoretry_for=(api.ParticulierApiUnavailable, api.ParticulierApiRateLimitExceeded),
    max_per_time_window=settings.PARTICULIER_API_RATE_LIMIT_THRESHOLD,
    time_window_size=settings.PARTICULIER_API_RATE_LIMIT_TIME_WINDOW_SECONDS,
)
def get_quotient_familial_task(payload: GetQutientFamilialTaskPayload) -> None:
    fraud_check = (
        db.session.query(subscription_models.BeneficiaryFraudCheck)
        .filter(
            subscription_models.BeneficiaryFraudCheck.id == payload.fraud_check_id,
            subscription_models.BeneficiaryFraudCheck.type == subscription_models.FraudCheckType.QF_BONUS_CREDIT,
        )
        .one()
    )
    if fraud_check.status != subscription_models.FraudCheckStatus.STARTED:
        logger.warning("Trying to handle already processed bonus fraud check #%s", payload.fraud_check_id)
        return
    source_data: QuotientFamilialBonusCreditContent = typing.cast(
        QuotientFamilialBonusCreditContent, fraud_check.source_data()
    )
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
        db.session.commit()
