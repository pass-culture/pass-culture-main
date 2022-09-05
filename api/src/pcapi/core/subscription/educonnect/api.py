import datetime
import logging
import typing

from pcapi.connectors.beneficiaries.educonnect import models as educonnect_models
from pcapi.core.fraud import api as fraud_api
from pcapi.core.fraud import models as fraud_models
import pcapi.core.mails.transactional as transactional_mails
from pcapi.core.subscription import api as subscription_api
from pcapi.core.subscription import models as subscription_models
from pcapi.core.users import external as users_external
from pcapi.core.users import models as users_models

from . import exceptions
from . import messages


logger = logging.getLogger(__name__)


def handle_educonnect_authentication(
    user: users_models.User, educonnect_user: educonnect_models.EduconnectUser
) -> list[fraud_models.FraudReasonCode]:
    educonnect_content = fraud_models.EduconnectContent(
        birth_date=educonnect_user.birth_date,
        civility=educonnect_user.civility if educonnect_user.civility else None,
        educonnect_id=educonnect_user.educonnect_id,
        first_name=educonnect_user.first_name,
        ine_hash=educonnect_user.ine_hash,
        last_name=educonnect_user.last_name,
        registration_datetime=datetime.datetime.utcnow(),
        school_uai=educonnect_user.school_uai,
        student_level=educonnect_user.student_level,
    )

    try:
        fraud_check = fraud_api.on_educonnect_result(user, educonnect_content)
    except Exception:
        logger.exception("Error on educonnect result", extra={"user_id": user.id})
        raise exceptions.EduconnectSubscriptionException()

    subscription_api.update_user_birth_date_if_not_beneficiary(user, fraud_check.source_data().get_birth_date())  # type: ignore [union-attr]

    if fraud_check.status == fraud_models.FraudCheckStatus.OK:
        try:
            is_activated = subscription_api.activate_beneficiary_if_no_missing_step(user=user)
        except Exception:
            logger.exception("Error while activating user from Educonnect", extra={"user_id": user.id})
            raise exceptions.EduconnectSubscriptionException()

        if not is_activated:
            users_external.update_external_user(user)
    else:
        _handle_validation_errors(user, fraud_check)
        logger.warning(
            "Fraud suspicion after educonnect authentication with codes: %s",
            (", ").join([code.value for code in fraud_check.reasonCodes]),  # type: ignore [union-attr]
            extra={"user_id": user.id},
        )

    return fraud_check.reasonCodes  # type: ignore [return-value]


def _handle_validation_errors(
    user: users_models.User,
    fraud_check: fraud_models.BeneficiaryFraudCheck,
) -> None:
    if fraud_models.FraudReasonCode.DUPLICATE_USER in fraud_check.reasonCodes:  # type: ignore [operator]
        transactional_mails.send_duplicate_beneficiary_email(user, fraud_check.source_data())  # type: ignore [arg-type]


def get_educonnect_subscription_item_status(
    user: users_models.User,
    eligibility: users_models.EligibilityType | None,
    educonnect_fraud_checks: list[fraud_models.BeneficiaryFraudCheck],
) -> subscription_models.SubscriptionItemStatus:
    """
    An educonnect failure is always retryable, as long as the user is eligible for UNDERAGE grant
    """
    if any(check.status == fraud_models.FraudCheckStatus.OK for check in educonnect_fraud_checks):
        return subscription_models.SubscriptionItemStatus.OK

    if (
        subscription_api.is_eligibility_activable(user, eligibility)
        and user.eligibility == users_models.EligibilityType.UNDERAGE
    ):
        return subscription_models.SubscriptionItemStatus.TODO

    return subscription_models.SubscriptionItemStatus.VOID


def get_educonnect_subscription_message(
    educonnect_fraud_check: fraud_models.BeneficiaryFraudCheck,
) -> subscription_models.SubscriptionMessage | None:
    if educonnect_fraud_check.status == fraud_models.FraudCheckStatus.OK:
        return None

    if educonnect_fraud_check.resultContent is None:
        birth_date = None
    else:
        content = typing.cast(fraud_models.EduconnectContent, educonnect_fraud_check.source_data())
        birth_date = content.get_birth_date()

    return messages.get_educonnect_failure_subscription_message(
        educonnect_fraud_check.reasonCodes or [], birth_date, educonnect_fraud_check.user.id
    )
