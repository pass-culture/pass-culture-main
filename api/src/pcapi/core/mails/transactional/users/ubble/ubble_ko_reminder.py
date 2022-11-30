import datetime
import logging

from dateutil.relativedelta import relativedelta

from pcapi import settings
from pcapi.core import mails
import pcapi.core.fraud.models as fraud_models
import pcapi.core.mails.models as mails_models
import pcapi.core.subscription.api as subscription_api
import pcapi.core.subscription.models as subscription_models
import pcapi.core.subscription.ubble.api as ubble_subscription
import pcapi.core.users.api as users_api
import pcapi.core.users.models as users_models

from . import constants


logger = logging.getLogger(__name__)


def send_ubble_ko_reminder_emails() -> None:
    users_with_fraud_check = _find_users_that_failed_ubble_check(days_ago=settings.UBBLE_KO_REMINDER_DELAY)
    for user, fraud_check in users_with_fraud_check:
        if fraud_check is None:
            continue

        reason_code = ubble_subscription.get_most_relevant_ubble_error(fraud_check)
        if not reason_code:
            logger.warning(
                "Could not find reason code for a user who failed ubble check",
                extra={"user_id": user.id},
            )
            continue

        data = _get_ubble_ko_reminder_email_data(reason_code)
        if not data:
            logger.warning("Could not find email template for reason code %s", reason_code)
            continue

        mails.send(recipients=[user.email], data=data)


def _get_ubble_ko_reminder_email_data(code: fraud_models.FraudReasonCode) -> mails_models.TransactionalEmailData | None:
    mapping = constants.ubble_error_to_email_mapping.get(code.value)
    if not mapping:
        return None

    template = mapping.reminder_template
    if not template:
        return None

    return mails_models.TransactionalEmailData(template=template.value)


def _find_users_that_failed_ubble_check(
    days_ago: int = 7,
) -> list[tuple[users_models.User, fraud_models.BeneficiaryFraudCheck | None]]:
    users = (
        users_models.User.query.join(users_models.User.beneficiaryFraudChecks)
        .filter(
            users_models.User.is_beneficiary == False,
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

    return [
        (user, _get_latest_failed_fraud_check(user))
        for user in users
        if users_api.is_eligible_for_beneficiary_upgrade(user, user.eligibility)
        and subscription_api.get_identity_check_subscription_status(user, user.eligibility)
        == subscription_models.SubscriptionItemStatus.TODO
    ]


def _get_latest_failed_fraud_check(user: users_models.User) -> fraud_models.BeneficiaryFraudCheck | None:
    ubble_ko_checks = [
        check
        for check in user.beneficiaryFraudChecks
        if check.type == fraud_models.FraudCheckType.UBBLE
        and check.status in [fraud_models.FraudCheckStatus.KO, fraud_models.FraudCheckStatus.SUSPICIOUS]
    ]

    return max(ubble_ko_checks, key=lambda fraud_check: fraud_check.dateCreated) if ubble_ko_checks else None
