import typing

from pcapi.core.fraud import models as fraud_models
from pcapi.core.subscription import messages as subscription_messages
from pcapi.core.subscription import models as subscription_models
from pcapi.core.users import constants as users_constants


def get_educonnect_failure_subscription_message(
    educonnect_fraud_check: fraud_models.BeneficiaryFraudCheck,
) -> subscription_models.SubscriptionMessage:
    reason_codes = educonnect_fraud_check.reasonCodes or []
    if educonnect_fraud_check.resultContent is not None:
        educonnect_content = typing.cast(fraud_models.EduconnectContent, educonnect_fraud_check.source_data())
        birth_date = educonnect_content.get_birth_date()
    else:
        educonnect_content = None
        birth_date = None

    if (
        fraud_models.FraudReasonCode.AGE_NOT_VALID in reason_codes
        or fraud_models.FraudReasonCode.NOT_ELIGIBLE in reason_codes
    ) and birth_date:
        user_message = f"Ton dossier a été refusé. La date de naissance sur ton compte Éduconnect ({birth_date.strftime('%d/%m/%Y')}) indique que tu n'as pas entre {users_constants.ELIGIBILITY_UNDERAGE_RANGE[0]} et {users_constants.ELIGIBILITY_UNDERAGE_RANGE[-1]} ans."

    elif fraud_models.FraudReasonCode.DUPLICATE_USER in reason_codes:
        user_message = subscription_messages.build_duplicate_error_message(
            educonnect_fraud_check.user, fraud_models.FraudReasonCode.DUPLICATE_USER, educonnect_content
        )

    elif fraud_models.FraudReasonCode.DUPLICATE_INE in reason_codes:
        user_message = subscription_messages.build_duplicate_error_message(
            educonnect_fraud_check.user, fraud_models.FraudReasonCode.DUPLICATE_INE, educonnect_content
        )

    else:
        user_message = "La vérification de ton identité a échoué. Tu peux réessayer."

    return subscription_models.SubscriptionMessage(
        user_message=user_message,
        call_to_action=subscription_messages.REDIRECT_TO_IDENTIFICATION_CHOICE,
        updated_at=educonnect_fraud_check.updatedAt,
    )
