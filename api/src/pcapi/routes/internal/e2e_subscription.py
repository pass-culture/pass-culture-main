import logging

import sqlalchemy as sa

from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription.bonus import tasks as bonus_tasks
from pcapi.models import db
from pcapi.routes.apis import private_api
from pcapi.routes.internal.auth import api_key_required
from pcapi.utils.transaction_manager import atomic


logger = logging.getLogger(__name__)


@private_api.route("/e2e/bonus_credit/<user_id>/recover", methods=["POST"])
@atomic()
@api_key_required
def recover_started_bonus_credit_applications(user_id: int) -> tuple[dict, int]:
    """
    Copy of bonus.tasks.recover_started_bonus_credit_applications with a few differences:
    - no cutoff time
    - a filter on user id
    """
    page_size = 200
    started_bonus_credit_fraud_check_stmt = sa.select(subscription_models.BeneficiaryFraudCheck).filter(
        subscription_models.BeneficiaryFraudCheck.type.in_(
            [
                subscription_models.FraudCheckType.QF_BONUS_CREDIT,
                subscription_models.FraudCheckType.AAH_BONUS_CREDIT,
                subscription_models.FraudCheckType.AEEH_BONUS_CREDIT,
            ]
        ),
        subscription_models.BeneficiaryFraudCheck.status == subscription_models.FraudCheckStatus.STARTED,
        subscription_models.BeneficiaryFraudCheck.userId == user_id,
    )
    started_bonus_credit_fraud_checks = db.session.scalars(started_bonus_credit_fraud_check_stmt).all()

    recovered_fraud_check_ids_by_type: dict[str, list[int]] = {
        subscription_models.FraudCheckType.QF_BONUS_CREDIT.value: [],
        subscription_models.FraudCheckType.AAH_BONUS_CREDIT.value: [],
        subscription_models.FraudCheckType.AEEH_BONUS_CREDIT.value: [],
    }

    expected_api_particulier_calls = 0
    for fraud_check in started_bonus_credit_fraud_checks:
        match fraud_check.type:
            case subscription_models.FraudCheckType.QF_BONUS_CREDIT:
                expected_api_particulier_calls += 12

                if expected_api_particulier_calls > page_size:
                    break

                payload = bonus_tasks.BonusTaskPayload(fraud_check_id=fraud_check.id)
                bonus_tasks.apply_for_quotient_familial_bonus_task.delay(payload=payload.model_dump())
                recovered_fraud_check_ids_by_type[subscription_models.FraudCheckType.QF_BONUS_CREDIT.value].append(
                    fraud_check.id
                )

            case subscription_models.FraudCheckType.AAH_BONUS_CREDIT:
                expected_api_particulier_calls += 1

                if expected_api_particulier_calls > page_size:
                    break

                payload = bonus_tasks.BonusTaskPayload(fraud_check_id=fraud_check.id)
                bonus_tasks.apply_for_adult_disability_bonus_task.delay(payload=payload.model_dump())
                recovered_fraud_check_ids_by_type[subscription_models.FraudCheckType.AAH_BONUS_CREDIT.value].append(
                    fraud_check.id
                )

            case subscription_models.FraudCheckType.AEEH_BONUS_CREDIT:
                expected_api_particulier_calls += 1

                if expected_api_particulier_calls > page_size:
                    break

                payload = bonus_tasks.BonusTaskPayload(fraud_check_id=fraud_check.id)
                bonus_tasks.apply_for_disabled_child_education_bonus_task.delay(payload=payload.model_dump())
                recovered_fraud_check_ids_by_type[subscription_models.FraudCheckType.AEEH_BONUS_CREDIT.value].append(
                    fraud_check.id
                )

            case _:
                logger.error("Unexpected %s fraud check %s was queried", fraud_check.type, fraud_check.id)

    return recovered_fraud_check_ids_by_type, 200
