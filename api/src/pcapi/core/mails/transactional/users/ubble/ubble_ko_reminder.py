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
    users = find_users_that_failed_ubble_check(days_ago=settings.UBBLE_KO_REMINDER_DELAY)
    users_by_reason_codes = sort_users_by_reason_codes(users)

    result = {}

    for reason_code, users in users_by_reason_codes.items():
        data = get_ubble_ko_reminder_email_data(reason_code)
        if not data:
            if reason_code == fraud_models.FraudReasonCode.NO_REASON_CODE:
                logger.warning(
                    "Could not find reason code for users that failed ubble check",
                    extra={"users": [user.id for user in users]},
                )
            else:
                logger.warning("Could not find email template for reason code %s", reason_code)
            continue

        result[reason_code] = mails.send(recipients=[user.email for user in users], data=data)

    if all(result.values()):
        logger.info("Sent all ubble ko reminder emails successfully", extra={"result": result})
    else:
        logger.info("Could not send some ubble ko reminder emails", extra={"result": result})


def get_ubble_ko_reminder_email_data(code: str) -> mails_models.TransactionalEmailData | None:
    mapping = constants.ubble_error_to_email_mapping.get(code)
    if not mapping:
        return None

    template = mapping.reminder_template
    if not template:
        return None

    return mails_models.TransactionalEmailData(template=template.value)


def find_users_that_failed_ubble_check(days_ago: int = 7) -> list[users_models.User]:
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
        user
        for user in users
        if users_api.is_eligible_for_beneficiary_upgrade(user, user.eligibility)
        and subscription_api.get_identity_check_subscription_status(user, user.eligibility)
        == subscription_models.SubscriptionItemStatus.TODO
    ]


def sort_users_by_reason_codes(users: list[users_models.User]) -> dict[str, list[users_models.User]]:
    users_by_reason_codes: dict[str, list[users_models.User]] = {}
    for user in users:
        latest_failed_ubble_check = next(
            (
                fraud_check
                for fraud_check in user.beneficiaryFraudChecks
                if fraud_check.type == fraud_models.FraudCheckType.UBBLE
                and (
                    fraud_check.status == fraud_models.FraudCheckStatus.KO
                    or fraud_check.status == fraud_models.FraudCheckStatus.SUSPICIOUS
                )
            ),
            None,
        )
        if latest_failed_ubble_check is None:
            users_by_reason_codes.setdefault(fraud_models.FraudReasonCode.NO_REASON_CODE, []).append(user)
            continue

        reason_code = ubble_subscription.get_most_relevant_ubble_error(latest_failed_ubble_check)

        users_by_reason_codes.setdefault(reason_code, []).append(user)
    return users_by_reason_codes
