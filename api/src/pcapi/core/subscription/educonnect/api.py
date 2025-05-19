import datetime
import logging

import pcapi.core.mails.transactional as transactional_mails
from pcapi.connectors.beneficiaries.educonnect import models as educonnect_models
from pcapi.core.external.attributes import api as external_attributes_api
from pcapi.core.fraud import api as fraud_api
from pcapi.core.fraud import models as fraud_models
from pcapi.core.subscription import api as subscription_api
from pcapi.core.subscription import models as subscription_models
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

    subscription_api.update_user_birth_date_if_not_beneficiary(user, educonnect_content.get_birth_date())

    if fraud_check.status == fraud_models.FraudCheckStatus.OK:
        try:
            is_activated = subscription_api.activate_beneficiary_if_no_missing_step(user=user)
        except Exception:
            logger.exception("Error while activating user from Educonnect", extra={"user_id": user.id})
            raise exceptions.EduconnectSubscriptionException()

        if not is_activated:
            external_attributes_api.update_external_user(user)
    else:
        if fraud_models.FraudReasonCode.DUPLICATE_USER in (fraud_check.reasonCodes or []):
            transactional_mails.send_duplicate_beneficiary_email(
                user, educonnect_content, fraud_models.FraudReasonCode.DUPLICATE_USER
            )

    return fraud_check.reasonCodes


def get_educonnect_subscription_message(
    educonnect_fraud_check: fraud_models.BeneficiaryFraudCheck,
) -> subscription_models.SubscriptionMessage | None:
    if educonnect_fraud_check.status == fraud_models.FraudCheckStatus.OK:
        return None

    return messages.get_educonnect_failure_subscription_message(educonnect_fraud_check)
