import collections
import datetime
import logging

from dateutil.relativedelta import relativedelta
import sqlalchemy as sqla

from pcapi import settings
from pcapi.core import mails
from pcapi.core.external.batch import bulk_track_ubble_ko_events
import pcapi.core.fraud.models as fraud_models
import pcapi.core.mails.models as mails_models
import pcapi.core.subscription.api as subscription_api
import pcapi.core.subscription.models as subscription_models
import pcapi.core.subscription.ubble.api as ubble_subscription
import pcapi.core.users.api as users_api
import pcapi.core.users.models as users_models

from . import constants


logger = logging.getLogger(__name__)


def send_reminder_emails() -> None:
    users_with_quick_actions = _find_users_to_remind(
        days_ago=settings.DAYS_BEFORE_UBBLE_QUICK_ACTION_REMINDER,
        reason_codes_filter=[
            fraud_models.FraudReasonCode.ID_CHECK_UNPROCESSABLE,
            fraud_models.FraudReasonCode.ID_CHECK_DATA_MATCH,
            fraud_models.FraudReasonCode.ID_CHECK_NOT_AUTHENTIC,
        ],
    )
    users_with_long_actions = _find_users_to_remind(
        days_ago=settings.DAYS_BEFORE_UBBLE_LONG_ACTION_REMINDER,
        reason_codes_filter=[
            fraud_models.FraudReasonCode.ID_CHECK_NOT_SUPPORTED,
            fraud_models.FraudReasonCode.ID_CHECK_EXPIRED,
        ],
    )

    users_to_notify_per_code = collections.defaultdict(list)

    for user, fraud_check_reason_codes in users_with_quick_actions + users_with_long_actions:
        relevant_reason_code = ubble_subscription.get_most_relevant_ubble_error(fraud_check_reason_codes)
        if not relevant_reason_code:
            logger.error(
                "Could not find reason code for a user who failed ubble check, to send reminder email",
                extra={"user_id": user.id},
            )
            continue

        email_data = _get_reminder_email_data(relevant_reason_code)
        if not email_data:
            logger.error("Could not find reminder email template for reason code %s", relevant_reason_code)
            continue

        users_to_notify_per_code[relevant_reason_code].append(user.id)
        mails.send(recipients=[user.email], data=email_data)

    bulk_track_ubble_ko_events(users_to_notify_per_code)


def _get_reminder_email_data(code: fraud_models.FraudReasonCode) -> mails_models.TransactionalEmailData | None:
    mapping = constants.ubble_error_to_email_mapping.get(code.value)
    if not mapping:
        return None

    template = mapping.reminder_template
    if not template:
        return None

    return mails_models.TransactionalEmailData(template=template.value)


def _find_users_to_remind(
    days_ago: int, reason_codes_filter: list[fraud_models.FraudReasonCode]
) -> list[tuple[users_models.User, list[fraud_models.FraudReasonCode]]]:
    users: list[users_models.User] = (
        users_models.User.query.join(users_models.User.beneficiaryFraudChecks)
        .filter(
            sqla.not_(users_models.User.is_beneficiary),
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

    users_with_reasons: list[tuple[users_models.User, list[fraud_models.FraudReasonCode]]] = []
    for user in users:
        if not (
            users_api.is_eligible_for_beneficiary_upgrade(user, user.eligibility)
            and subscription_api.get_user_subscription_state(user).fraud_status
            == subscription_models.SubscriptionItemStatus.TODO
        ):
            continue
        latest_fraud_check_reason_codes = _get_latest_failed_ubble_fraud_check(user).reasonCodes or []

        if set(latest_fraud_check_reason_codes) & set(reason_codes_filter):
            users_with_reasons.append((user, latest_fraud_check_reason_codes))

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
