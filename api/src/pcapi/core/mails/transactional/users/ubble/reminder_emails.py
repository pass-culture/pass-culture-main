import datetime
import logging

from dateutil.relativedelta import relativedelta
import sqlalchemy as sa

from pcapi import settings
import pcapi.core.fraud.models as fraud_models
import pcapi.core.fraud.ubble.constants as ubble_constants
from pcapi.core.mails.transactional import send_subscription_document_error_email
import pcapi.core.subscription.api as subscription_api
import pcapi.core.subscription.models as subscription_models
import pcapi.core.subscription.ubble.api as ubble_subscription
import pcapi.core.users.api as users_api
import pcapi.core.users.models as users_models


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
    days_ago: int, reason_codes_filter: list[fraud_models.FraudReasonCode]
) -> list[tuple[users_models.User, fraud_models.FraudReasonCode]]:
    users: list[users_models.User] = (
        users_models.User.query.join(users_models.User.beneficiaryFraudChecks)
        .filter(
            sa.not_(users_models.User.is_beneficiary),
            fraud_models.BeneficiaryFraudCheck.type == fraud_models.FraudCheckType.UBBLE,
            fraud_models.BeneficiaryFraudCheck.status.in_(
                [fraud_models.FraudCheckStatus.KO, fraud_models.FraudCheckStatus.SUSPICIOUS]
            ),
            fraud_models.BeneficiaryFraudCheck.dateCreated < datetime.datetime.utcnow() - relativedelta(days=days_ago),
            fraud_models.BeneficiaryFraudCheck.dateCreated
            >= datetime.datetime.utcnow() - relativedelta(days=days_ago + 1),
        )
        .all()
    )

    users_with_reasons: list[tuple[users_models.User, fraud_models.FraudReasonCode]] = []
    for user in users:
        if not (
            users_api.is_eligible_for_beneficiary_upgrade(user, user.eligibility)
            and subscription_api.get_user_subscription_state(user).fraud_status
            == subscription_models.SubscriptionItemStatus.TODO
        ):
            continue
        latest_fraud_check_reason_codes = _get_latest_failed_ubble_fraud_check(user).reasonCodes or []

        relevant_reason_code = ubble_subscription.get_most_relevant_ubble_error(latest_fraud_check_reason_codes)
        if relevant_reason_code in reason_codes_filter:
            users_with_reasons.append((user, relevant_reason_code))

    return users_with_reasons


def _get_latest_failed_ubble_fraud_check(user: users_models.User) -> fraud_models.BeneficiaryFraudCheck:
    ubble_ko_checks = [
        check
        for check in user.beneficiaryFraudChecks
        if check.type == fraud_models.FraudCheckType.UBBLE
        and check.status in [fraud_models.FraudCheckStatus.KO, fraud_models.FraudCheckStatus.SUSPICIOUS]
    ]
    if not ubble_ko_checks:
        raise ValueError("User has no failed ubble fraud check")

    return max(ubble_ko_checks, key=lambda fraud_check: fraud_check.dateCreated)
