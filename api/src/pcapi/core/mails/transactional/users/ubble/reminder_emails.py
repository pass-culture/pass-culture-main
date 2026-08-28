import logging

import sqlalchemy as sa
from dateutil.relativedelta import relativedelta

import pcapi.core.subscription.api as subscription_api
import pcapi.core.subscription.models as subscription_models
import pcapi.core.subscription.schemas as subscription_schemas
import pcapi.core.subscription.ubble.api as ubble_api
import pcapi.core.subscription.ubble.constants as ubble_constants
import pcapi.core.users.models as users_models
from pcapi import settings
from pcapi.core.mails.transactional import send_subscription_document_error_email
from pcapi.core.users import eligibility_api
from pcapi.models import db
from pcapi.utils import date as date_utils


logger = logging.getLogger(__name__)


def send_reminders() -> None:
    users_with_quick_actions = _find_users_to_remind(
        days_ago=settings.DAYS_BEFORE_UBBLE_QUICK_ACTION_REMINDER,
        reason_codes_filter=list(ubble_constants.REASON_CODES_FOR_QUICK_ACTION_REMINDERS),
    )
    users_with_long_actions = _find_users_to_remind(
        days_ago=settings.DAYS_BEFORE_UBBLE_LONG_ACTION_REMINDER,
        reason_codes_filter=list(ubble_constants.REASON_CODES_FOR_LONG_ACTION_REMINDERS),
    )

    for user, relevant_reason_code in users_with_quick_actions + users_with_long_actions:
        if not relevant_reason_code:
            logger.error(
                "Could not find reason code for a user who failed ubble check, to send reminder email",
                extra={"user_id": user.id},
            )
            continue

        send_subscription_document_error_email(user.email, relevant_reason_code, is_reminder=True)


def _find_users_to_remind(
    days_ago: int, reason_codes_filter: list[subscription_models.FraudReasonCode]
) -> list[tuple[users_models.User, subscription_models.FraudReasonCode]]:
    users: list[users_models.User] = (
        db.session.query(users_models.User)
        .join(users_models.User.beneficiaryFraudChecks)
        .filter(
            sa.not_(users_models.User.is_beneficiary),
            subscription_models.BeneficiaryFraudCheck.type == subscription_models.FraudCheckType.UBBLE,
            subscription_models.BeneficiaryFraudCheck.status.in_(
                [subscription_models.FraudCheckStatus.KO, subscription_models.FraudCheckStatus.SUSPICIOUS]
            ),
            subscription_models.BeneficiaryFraudCheck.dateCreated
            < date_utils.get_naive_utc_now() - relativedelta(days=days_ago),
            subscription_models.BeneficiaryFraudCheck.dateCreated
            >= date_utils.get_naive_utc_now() - relativedelta(days=days_ago + 1),
        )
        .all()
    )

    users_with_reasons: list[tuple[users_models.User, subscription_models.FraudReasonCode]] = []
    for user in users:
        if not (
            eligibility_api.is_eligible_for_next_recredit_activation_steps(user)
            and subscription_api.get_user_subscription_state(user).fraud_status
            == subscription_schemas.SubscriptionItemStatus.TODO
        ):
            continue
        latest_fraud_check_reason_codes = _get_latest_failed_ubble_fraud_check(user).reasonCodes or []

        relevant_reason_code = ubble_api.get_most_relevant_ubble_error(latest_fraud_check_reason_codes)
        if relevant_reason_code in reason_codes_filter:
            users_with_reasons.append((user, relevant_reason_code))

    return users_with_reasons


def _get_latest_failed_ubble_fraud_check(user: users_models.User) -> subscription_models.BeneficiaryFraudCheck:
    ubble_ko_checks = [
        check
        for check in user.beneficiaryFraudChecks
        if check.type == subscription_models.FraudCheckType.UBBLE
        and check.status in [subscription_models.FraudCheckStatus.KO, subscription_models.FraudCheckStatus.SUSPICIOUS]
    ]
    if not ubble_ko_checks:
        raise ValueError("User has no failed ubble fraud check")

    return max(ubble_ko_checks, key=lambda fraud_check: fraud_check.dateCreated)
