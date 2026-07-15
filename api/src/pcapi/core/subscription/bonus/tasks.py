import datetime
import logging

import sqlalchemy as sa
from dateutil.relativedelta import relativedelta
from pydantic import BaseModel as BaseModelV2

from pcapi import settings
from pcapi.celery_tasks.tasks import celery_async_task
from pcapi.connectors import api_particulier
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription.bonus.api import apply_for_adult_disability_bonus
from pcapi.core.subscription.bonus.api import apply_for_disabled_child_education_bonus
from pcapi.core.subscription.bonus.api import apply_for_quotient_familial_bonus
from pcapi.models import db


logger = logging.getLogger(__name__)


# the task calls the quotient familial endpoint for each month of a year
QUOTIENT_FAMILIAL_TASK_RATE_LIMIT = settings.PARTICULIER_API_RATE_LIMIT_THRESHOLD // 12


class BonusTaskPayload(BaseModelV2):
    fraud_check_id: int


@celery_async_task(
    name="tasks.api_particulier.default.apply_for_quotient_familial_bonus",
    model=BonusTaskPayload,
    autoretry_for=(api_particulier.ParticulierApiUnavailable, api_particulier.ParticulierApiRateLimitExceeded),
    rate_limit="200/m",
)
def apply_for_quotient_familial_bonus_task(payload: BonusTaskPayload) -> None:
    fraud_check = (
        db.session.query(subscription_models.BeneficiaryFraudCheck)
        .filter(
            subscription_models.BeneficiaryFraudCheck.id == payload.fraud_check_id,
        )
        .one_or_none()
    )
    if fraud_check is None:
        logger.warning("fraud check %s was deleted before a celery worker could pick it up", payload.fraud_check_id)
        return

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


@celery_async_task(
    name="tasks.api_particulier.default.apply_for_adult_disability_bonus",
    model=BonusTaskPayload,
    autoretry_for=(api_particulier.ParticulierApiUnavailable, api_particulier.ParticulierApiRateLimitExceeded),
    rate_limit="200/m",
)
def apply_for_adult_disability_bonus_task(payload: BonusTaskPayload) -> None:
    fraud_check = (
        db.session.query(subscription_models.BeneficiaryFraudCheck)
        .filter(
            subscription_models.BeneficiaryFraudCheck.id == payload.fraud_check_id,
        )
        .one_or_none()
    )
    if fraud_check is None:
        logger.warning("fraud check %s was deleted before a celery worker could pick it up", payload.fraud_check_id)
        return

    if fraud_check.type != subscription_models.FraudCheckType.AAH_BONUS_CREDIT:
        logger.error(
            "Trying to fetch FraudCheck #%s of type AAH_BONUS_CREDIT resulted in a FraudCheck of type %s",
            fraud_check.id,
            fraud_check.type,
        )
        return

    if fraud_check.status != subscription_models.FraudCheckStatus.STARTED:
        logger.warning("Trying to handle already processed bonus fraud check #%s", payload.fraud_check_id)
        return

    apply_for_adult_disability_bonus(fraud_check)


@celery_async_task(
    name="tasks.api_particulier.default.apply_for_disabled_child_education_bonus",
    model=BonusTaskPayload,
    autoretry_for=(api_particulier.ParticulierApiUnavailable, api_particulier.ParticulierApiRateLimitExceeded),
    rate_limit="200/m",
)
def apply_for_disabled_child_education_bonus_task(payload: BonusTaskPayload) -> None:
    fraud_check = (
        db.session.query(subscription_models.BeneficiaryFraudCheck)
        .filter(
            subscription_models.BeneficiaryFraudCheck.id == payload.fraud_check_id,
        )
        .one_or_none()
    )
    if fraud_check is None:
        logger.warning("fraud check %s was deleted before a celery worker could pick it up", payload.fraud_check_id)
        return

    if fraud_check.type != subscription_models.FraudCheckType.AEEH_BONUS_CREDIT:
        logger.error(
            "Trying to fetch FraudCheck #%s of type AEEH_BONUS_CREDIT resulted in a FraudCheck of type %s",
            fraud_check.id,
            fraud_check.type,
        )
        return

    if fraud_check.status != subscription_models.FraudCheckStatus.STARTED:
        logger.warning("Trying to handle already processed bonus fraud check #%s", payload.fraud_check_id)
        return

    apply_for_disabled_child_education_bonus(fraud_check)


def recover_started_bonus_credit_applications(page_size: int = 200) -> None:
    """
    Recovers the `page_size` first started QF/AAH/AEEH fraud checks.
    This function only recovers the first page, and is meant to be called as often as needed by recovery workers,
    but no more than once per minute for rate limit reasons.
    """
    cutoff_time = datetime.datetime.now(tz=None) - relativedelta(seconds=settings.BONUS_CREDIT_DELAY)
    started_bonus_credit_fraud_check_stmt = (
        sa.select(subscription_models.BeneficiaryFraudCheck)
        .filter(
            subscription_models.BeneficiaryFraudCheck.type.in_(
                [
                    subscription_models.FraudCheckType.QF_BONUS_CREDIT,
                    subscription_models.FraudCheckType.AAH_BONUS_CREDIT,
                    subscription_models.FraudCheckType.AEEH_BONUS_CREDIT,
                ]
            ),
            subscription_models.BeneficiaryFraudCheck.status == subscription_models.FraudCheckStatus.STARTED,
            subscription_models.BeneficiaryFraudCheck.updatedAt <= cutoff_time,
        )
        .order_by(subscription_models.BeneficiaryFraudCheck.id)
        .limit(page_size)
    )
    started_bonus_credit_fraud_checks = db.session.scalars(started_bonus_credit_fraud_check_stmt).all()

    expected_api_particulier_calls = 0
    for fraud_check in started_bonus_credit_fraud_checks:
        match fraud_check.type:
            case subscription_models.FraudCheckType.QF_BONUS_CREDIT:
                expected_api_particulier_calls += 12

                if expected_api_particulier_calls > page_size:
                    return

                payload = BonusTaskPayload(fraud_check_id=fraud_check.id)
                apply_for_quotient_familial_bonus_task.delay(payload=payload.model_dump())

            case subscription_models.FraudCheckType.AAH_BONUS_CREDIT:
                expected_api_particulier_calls += 1

                if expected_api_particulier_calls > page_size:
                    return

                payload = BonusTaskPayload(fraud_check_id=fraud_check.id)
                apply_for_adult_disability_bonus_task.delay(payload=payload.model_dump())

            case subscription_models.FraudCheckType.AEEH_BONUS_CREDIT:
                expected_api_particulier_calls += 1

                if expected_api_particulier_calls > page_size:
                    return

                payload = BonusTaskPayload(fraud_check_id=fraud_check.id)
                apply_for_disabled_child_education_bonus_task.delay(payload=payload.model_dump())

            case _:
                logger.error("Unexpected %s fraud check %s was queried", fraud_check.type, fraud_check.id)
