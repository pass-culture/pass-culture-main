import datetime
import logging

import sqlalchemy as sa
from dateutil.relativedelta import relativedelta
from pydantic import BaseModel as BaseModelV2

from pcapi import settings
from pcapi.celery_tasks.tasks import celery_async_task
from pcapi.connectors import api_particulier
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription.bonus import constants as bonus_constants
from pcapi.core.subscription.bonus.api import apply_for_adult_disability_bonus
from pcapi.core.subscription.bonus.api import apply_for_disabled_child_education_bonus
from pcapi.core.subscription.bonus.api import apply_for_quotient_familial_bonus
from pcapi.models import db
from pcapi.models.feature import FeatureToggle
from pcapi.utils import date as date_utils
from pcapi.utils.transaction_manager import atomic


logger = logging.getLogger(__name__)


class BonusTaskPayload(BaseModelV2):
    fraud_check_id: int


RETRYABLE_EXCEPTIONS = (
    api_particulier.ParticulierApiRateLimitExceeded,
    api_particulier.ParticulierApiRequestConflict,
)


@celery_async_task(
    name="tasks.api_particulier.default.apply_for_quotient_familial_bonus",
    model=BonusTaskPayload,
    autoretry_for=RETRYABLE_EXCEPTIONS,
    retry_backoff=api_particulier.RATE_LIMIT_TIME_WINDOW_SIZE,
    retry_backoff_max=api_particulier.RATE_LIMIT_TIME_WINDOW_SIZE * 4,
    max_retries=3,
)
def apply_for_quotient_familial_bonus_task(payload: BonusTaskPayload) -> None:
    if not FeatureToggle.ENABLE_BONUS_CREDIT.is_active():
        logger.error("Trying to call apply_for_quotient_familial_bonus_task with disabled FF")
        return

    fraud_check = _get_bonus_fraud_check_to_handle(
        payload.fraud_check_id, subscription_models.FraudCheckType.QF_BONUS_CREDIT
    )
    if not fraud_check:
        return

    user = fraud_check.user
    is_last_attempt = _is_last_attempt(fraud_check)
    try:
        apply_for_quotient_familial_bonus(fraud_check)
    except (sa.orm.exc.ObjectDeletedError, sa.orm.exc.StaleDataError):
        if not user.received_bonus_credit:
            raise
    except Exception as e:
        is_time_sensitive_exception = isinstance(
            e, (api_particulier.ParticulierApiRequestConflict, api_particulier.ParticulierApiRateLimitExceeded)
        )
        with atomic():
            if not fraud_check.resultContent:
                fraud_check.resultContent = {}

            should_give_up = not is_time_sensitive_exception and is_last_attempt
            if should_give_up:
                fraud_check.status = subscription_models.FraudCheckStatus.ERROR
            else:
                fraud_check.resultContent["next_retry_at"] = date_utils.get_naive_utc_now() + relativedelta(hours=23)

        raise


@celery_async_task(
    name="tasks.api_particulier.default.apply_for_adult_disability_bonus",
    model=BonusTaskPayload,
    autoretry_for=RETRYABLE_EXCEPTIONS,
    retry_backoff=api_particulier.RATE_LIMIT_TIME_WINDOW_SIZE,
    retry_backoff_max=api_particulier.RATE_LIMIT_TIME_WINDOW_SIZE * 4,
    max_retries=3,
)
def apply_for_adult_disability_bonus_task(payload: BonusTaskPayload) -> None:
    if not FeatureToggle.ENABLE_BONUS_CREDIT.is_active():
        logger.error("Trying to call apply_for_adult_disability_bonus_task with disabled FF")
        return

    fraud_check = _get_bonus_fraud_check_to_handle(
        payload.fraud_check_id, subscription_models.FraudCheckType.AAH_BONUS_CREDIT
    )
    if not fraud_check:
        return

    user = fraud_check.user
    is_last_attempt = _is_last_attempt(fraud_check)
    try:
        apply_for_adult_disability_bonus(fraud_check)
    except (sa.orm.exc.ObjectDeletedError, sa.orm.exc.StaleDataError):
        if not user.received_bonus_credit:
            raise
    except Exception as e:
        is_time_sensitive_exception = isinstance(
            e, (api_particulier.ParticulierApiRequestConflict, api_particulier.ParticulierApiRateLimitExceeded)
        )
        with atomic():
            if not fraud_check.resultContent:
                fraud_check.resultContent = {}

            should_give_up = not is_time_sensitive_exception and is_last_attempt
            if should_give_up:
                fraud_check.status = subscription_models.FraudCheckStatus.ERROR
            else:
                fraud_check.resultContent["next_retry_at"] = date_utils.get_naive_utc_now() + relativedelta(hours=23)

        raise


@celery_async_task(
    name="tasks.api_particulier.default.apply_for_disabled_child_education_bonus",
    model=BonusTaskPayload,
    autoretry_for=RETRYABLE_EXCEPTIONS,
    retry_backoff=api_particulier.RATE_LIMIT_TIME_WINDOW_SIZE,
    retry_backoff_max=api_particulier.RATE_LIMIT_TIME_WINDOW_SIZE * 4,
    max_retries=3,
)
def apply_for_disabled_child_education_bonus_task(payload: BonusTaskPayload) -> None:
    if not FeatureToggle.ENABLE_BONUS_CREDIT.is_active():
        logger.error("Trying to call apply_for_disabled_child_education_bonus_task with disabled FF")
        return

    fraud_check = _get_bonus_fraud_check_to_handle(
        payload.fraud_check_id, subscription_models.FraudCheckType.AEEH_BONUS_CREDIT
    )
    if not fraud_check:
        return

    user = fraud_check.user
    is_last_attempt = _is_last_attempt(fraud_check)
    try:
        apply_for_disabled_child_education_bonus(fraud_check)
    except (sa.orm.exc.ObjectDeletedError, sa.orm.exc.StaleDataError):
        if not user.received_bonus_credit:
            raise
    except Exception as e:
        is_time_sensitive_exception = isinstance(
            e, (api_particulier.ParticulierApiRequestConflict, api_particulier.ParticulierApiRateLimitExceeded)
        )
        with atomic():
            if not fraud_check.resultContent:
                fraud_check.resultContent = {}

            should_give_up = not is_time_sensitive_exception and is_last_attempt
            if should_give_up:
                fraud_check.status = subscription_models.FraudCheckStatus.ERROR
            else:
                fraud_check.resultContent["next_retry_at"] = date_utils.get_naive_utc_now() + relativedelta(hours=23)

        raise


def _get_bonus_fraud_check_to_handle(
    fraud_check_id: int, expected_type: subscription_models.FraudCheckType
) -> subscription_models.BeneficiaryFraudCheck | None:
    fraud_check = (
        db.session.query(subscription_models.BeneficiaryFraudCheck)
        .filter(
            subscription_models.BeneficiaryFraudCheck.id == fraud_check_id,
        )
        .options(sa.orm.joinedload(subscription_models.BeneficiaryFraudCheck.user))
        .one_or_none()
    )
    if fraud_check is None:
        logger.warning("fraud check %s was deleted before a celery worker could pick it up", fraud_check_id)
        return None

    if fraud_check.type != expected_type:
        logger.error(
            "Trying to fetch FraudCheck #%s of type %s resulted in a FraudCheck of type %s",
            fraud_check.id,
            expected_type.name,
            fraud_check.type,
        )
        return None

    if fraud_check.status != subscription_models.FraudCheckStatus.STARTED:
        logger.warning("Trying to handle already processed bonus fraud check #%s", fraud_check_id)
        return None

    return fraud_check


def _is_last_attempt(fraud_check: subscription_models.BeneficiaryFraudCheck) -> bool:
    if not fraud_check.resultContent:
        fraud_check.resultContent = {}

    error_code = fraud_check.resultContent.get("error_code")
    retry_at = fraud_check.resultContent.get("next_retry_at")

    has_already_failed = error_code is not None
    was_retried_enough = retry_at is not None and (
        datetime.datetime.fromisoformat(retry_at) - fraud_check.dateCreated
    ) > datetime.timedelta(days=7)
    return has_already_failed and was_retried_enough


def recover_started_bonus_credit_applications(
    user_id: int | None = None,
    cutoff_time: datetime.datetime | None = None,
    page_size: int = settings.PARTICULIER_API_RATE_LIMIT_THRESHOLD // 2,
) -> list[subscription_models.BeneficiaryFraudCheck]:
    """
    Recovers the `page_size` first started QF/AAH/AEEH fraud checks.
    This function only recovers the first page, and is meant to be called as often as needed by recovery workers.
    """
    if not FeatureToggle.ENABLE_BONUS_CREDIT.is_active():
        logger.warning("Trying to call recover_started_bonus_credit_applications with disabled FF")
        return []

    started_bonus_fraud_check_stmt = sa.select(subscription_models.BeneficiaryFraudCheck).filter(
        subscription_models.BeneficiaryFraudCheck.type.in_(
            [
                subscription_models.FraudCheckType.QF_BONUS_CREDIT,
                subscription_models.FraudCheckType.AAH_BONUS_CREDIT,
                subscription_models.FraudCheckType.AEEH_BONUS_CREDIT,
            ]
        ),
        subscription_models.BeneficiaryFraudCheck.status == subscription_models.FraudCheckStatus.STARTED,
    )
    if user_id:
        started_bonus_fraud_check_stmt = started_bonus_fraud_check_stmt.filter(
            subscription_models.BeneficiaryFraudCheck.userId == user_id
        )
    if cutoff_time:
        started_bonus_fraud_check_stmt = started_bonus_fraud_check_stmt.filter(
            subscription_models.BeneficiaryFraudCheck.resultContent.is_not(None),
            subscription_models.BeneficiaryFraudCheck.resultContent["next_retry_at"].astext.cast(sa.DateTime)
            <= cutoff_time,
        )

    keyset_paginated_stmt = started_bonus_fraud_check_stmt.order_by(subscription_models.BeneficiaryFraudCheck.id).limit(
        page_size
    )
    started_bonus_credit_fraud_checks = db.session.scalars(keyset_paginated_stmt).all()

    handled_fraud_checks: list[subscription_models.BeneficiaryFraudCheck] = []
    disability_fraud_check_user_ids: set[int] = set()
    expected_api_particulier_calls = 0.0
    for fraud_check in started_bonus_credit_fraud_checks:
        match fraud_check.type:
            case subscription_models.FraudCheckType.QF_BONUS_CREDIT:
                expected_api_particulier_calls += bonus_constants.EXPECTED_QUOTIENT_FAMILIAL_CALLS

                if expected_api_particulier_calls > page_size:
                    return handled_fraud_checks

                payload = BonusTaskPayload(fraud_check_id=fraud_check.id)
                apply_for_quotient_familial_bonus_task.delay(payload=payload.model_dump())
                handled_fraud_checks.append(fraud_check)

            case subscription_models.FraudCheckType.AAH_BONUS_CREDIT:
                expected_api_particulier_calls += 1

                if expected_api_particulier_calls > page_size:
                    return handled_fraud_checks

                is_other_disability_bonus_ongoing = fraud_check.userId in disability_fraud_check_user_ids
                if is_other_disability_bonus_ongoing:
                    # accessing AAH and AEEH of the same person at the same time crashes API Particulier
                    countdown = bonus_constants.DISABILITY_COUNTDOWN
                else:
                    countdown = 0

                disability_fraud_check_user_ids.add(fraud_check.userId)
                payload = BonusTaskPayload(fraud_check_id=fraud_check.id)
                apply_for_adult_disability_bonus_task.apply_async((payload.model_dump(),), countdown=countdown)
                handled_fraud_checks.append(fraud_check)

            case subscription_models.FraudCheckType.AEEH_BONUS_CREDIT:
                expected_api_particulier_calls += 1

                if expected_api_particulier_calls > page_size:
                    return handled_fraud_checks

                is_other_disability_bonus_ongoing = fraud_check.userId in disability_fraud_check_user_ids
                if is_other_disability_bonus_ongoing:
                    # accessing AAH and AEEH of the same person at the same time crashes API Particulier
                    countdown = bonus_constants.DISABILITY_COUNTDOWN
                else:
                    countdown = 0

                disability_fraud_check_user_ids.add(fraud_check.userId)
                payload = BonusTaskPayload(fraud_check_id=fraud_check.id)
                apply_for_disabled_child_education_bonus_task.apply_async((payload.model_dump(),), countdown=countdown)
                handled_fraud_checks.append(fraud_check)

            case _:
                logger.error("Unexpected %s fraud check %s was queried", fraud_check.type, fraud_check.id)

    return handled_fraud_checks
