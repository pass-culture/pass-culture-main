from datetime import datetime
import logging

from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import joinedload

from pcapi.core.fraud import models as fraud_models
from pcapi.core.mails.transactional.users.recredit_to_underage_beneficiary import (
    send_recredit_email_to_underage_beneficiary,
)
from pcapi.core.payments import models as payments_models
import pcapi.core.payments.conf as deposit_conf
from pcapi.core.users import external as users_external
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.repository import transaction


logger = logging.getLogger(__name__)

RECREDIT_BATCH_SIZE = 1000


def has_celebrated_birthday_since_registration(user: users_models.User) -> bool:
    user_identity_fraud_checks = [
        fraud_check
        for fraud_check in user.beneficiaryFraudChecks
        if fraud_check.type in fraud_models.IDENTITY_CHECK_TYPES
    ]
    ordered_fraud_checks = sorted(user_identity_fraud_checks, key=lambda fraud_check: fraud_check.dateCreated)
    if not ordered_fraud_checks:
        return False

    first_fraud_check = ordered_fraud_checks[0]
    try:
        first_fraud_check_registration_datetime = first_fraud_check.source_data().get_registration_datetime()
    except ValueError:  # This will happen for older Educonnect fraud checks that do not have registration date in their content
        if first_fraud_check.type == fraud_models.FraudCheckType.EDUCONNECT:
            first_fraud_check_registration_datetime = first_fraud_check.dateCreated
        else:
            logger.warning("Could not get registration date for fraud check %s", first_fraud_check.id)
            return False

    if first_fraud_check_registration_datetime is None:
        first_fraud_check_registration_datetime = first_fraud_check.dateCreated

    return first_fraud_check_registration_datetime.date() < user.latest_birthday


def can_be_recredited(user: users_models.User) -> bool:
    return (
        user.deposit_activation_date is not None
        and has_celebrated_birthday_since_registration(user)
        and not has_been_recredited(user)
    )


def has_been_recredited(user: users_models.User) -> bool:
    if user.deposit is None:
        return False
    if len(user.deposit.recredits) == 0:
        return False

    sorted_recredits = sorted(user.deposit.recredits, key=lambda recredit: recredit.dateCreated)
    return sorted_recredits[-1].recreditType == deposit_conf.RECREDIT_TYPE_AGE_MAPPING[user.age]


def recredit_underage_users() -> None:
    sixteen_years_ago = datetime.utcnow() - relativedelta(years=16)
    eighteen_years_ago = datetime.utcnow() - relativedelta(years=18)

    user_ids = [
        result
        for result, in (
            users_models.User.query.filter(users_models.User.has_underage_beneficiary_role)
            .filter(users_models.User.dateOfBirth > eighteen_years_ago)
            .filter(users_models.User.dateOfBirth <= sixteen_years_ago)
            .with_entities(users_models.User.id)
            .all()
        )
    ]

    start_index = 0
    total_users_recredited = 0

    while start_index < len(user_ids):
        users = (
            users_models.User.query.filter(
                users_models.User.id.in_(user_ids[start_index : start_index + RECREDIT_BATCH_SIZE])
            )
            .options(joinedload(users_models.User.deposits).joinedload(payments_models.Deposit.recredits))
            .all()
        )

        users_to_recredit = [user for user in users if can_be_recredited(user)]
        users_and_recredit_amounts = []
        with transaction():
            for user in users_to_recredit:
                recredit = payments_models.Recredit(
                    deposit=user.deposit,
                    amount=deposit_conf.RECREDIT_TYPE_AMOUNT_MAPPING[deposit_conf.RECREDIT_TYPE_AGE_MAPPING[user.age]],
                    recreditType=deposit_conf.RECREDIT_TYPE_AGE_MAPPING[user.age],
                )
                users_and_recredit_amounts.append((user, recredit.amount))
                recredit.deposit.amount += recredit.amount
                user.recreditAmountToShow = recredit.amount if recredit.amount > 0 else None

                db.session.add(user)
                db.session.add(recredit)
                total_users_recredited += 1

        logger.info("Recredited %s underage users deposits", len(users_to_recredit))

        for user, recredit_amount in users_and_recredit_amounts:
            users_external.update_external_user(user)
            if not send_recredit_email_to_underage_beneficiary(user, recredit_amount):
                logger.error("Failed to send recredit email to: %s", user.email)

        start_index += RECREDIT_BATCH_SIZE
    logger.info("Recredited %s users successfully", total_users_recredited)
