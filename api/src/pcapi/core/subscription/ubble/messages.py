import datetime
import typing

from pcapi.core.fraud import models as fraud_models
from pcapi.core.fraud.common import models as common_fraud_models
from pcapi.core.subscription import messages as subscription_messages
from pcapi.core.subscription import models as subscription_models

from . import models


REDIRECT_TO_IDENTIFICATION = subscription_models.CallToActionMessage(
    title="Réessayer la vérification de mon identité",
    link="passculture://verification-identite/identification",
    icon=subscription_models.CallToActionIcon.RETRY,
)


def _get_relevant_reason_code(reason_codes: list[fraud_models.FraudReasonCode]) -> fraud_models.FraudReasonCode | None:
    relevant = None
    if reason_codes:
        sorted_reason_codes = sorted(
            reason_codes,
            key=lambda rc: models.UBBLE_CODE_ERROR_MAPPING[rc].priority if rc in models.UBBLE_CODE_ERROR_MAPPING else 0,
            reverse=True,
        )
        relevant = sorted_reason_codes[0]
    return relevant


def get_application_pending_message(updated_at: datetime.datetime | None) -> subscription_models.SubscriptionMessage:
    return subscription_models.SubscriptionMessage(
        user_message="Ton document d'identité est en cours de vérification.",
        call_to_action=None,
        pop_over_icon=subscription_models.PopOverIcon.CLOCK,
        updated_at=updated_at,
    )


def get_ubble_retryable_message(
    reason_codes: list[fraud_models.FraudReasonCode], updated_at: datetime.datetime | None
) -> subscription_models.SubscriptionMessage:
    relevant_reason_code = _get_relevant_reason_code(reason_codes)
    if relevant_reason_code in models.UBBLE_CODE_ERROR_MAPPING:
        relevant_error = models.UBBLE_CODE_ERROR_MAPPING[relevant_reason_code]
    else:
        relevant_error = models.UBBLE_DEFAULT

    return subscription_models.SubscriptionMessage(
        user_message=relevant_error.retryable_user_message,
        message_summary=relevant_error.retryable_message_summary,
        action_hint=relevant_error.retryable_action_hint,
        call_to_action=subscription_messages.REDIRECT_TO_IDENTIFICATION_CHOICE,
        pop_over_icon=None,
        updated_at=updated_at,
    )


def get_ubble_not_retryable_message(
    fraud_check: fraud_models.BeneficiaryFraudCheck,
) -> subscription_models.SubscriptionMessage:
    reason_codes = fraud_check.reasonCodes or []
    relevant_reason_code = _get_relevant_reason_code(reason_codes)
    if relevant_reason_code in models.UBBLE_CODE_ERROR_MAPPING:
        relevant_error = models.UBBLE_CODE_ERROR_MAPPING[relevant_reason_code]
    else:
        relevant_error = models.UBBLE_DEFAULT

    user_message = relevant_error.not_retryable_user_message

    pop_over_icon = None
    call_to_action = None

    if relevant_reason_code in (
        fraud_models.FraudReasonCode.DUPLICATE_USER,
        fraud_models.FraudReasonCode.DUPLICATE_ID_PIECE_NUMBER,
    ):
        identity_content = (
            typing.cast(common_fraud_models.IdentityCheckContent, fraud_check.source_data())
            if fraud_check.resultContent
            else None
        )
        user_message = subscription_messages.build_duplicate_error_message(
            fraud_check.user, relevant_reason_code, identity_content
        )
        call_to_action = subscription_messages.compute_support_call_to_action(fraud_check.user.id)

    elif relevant_reason_code in (
        fraud_models.FraudReasonCode.AGE_TOO_OLD,
        fraud_models.FraudReasonCode.AGE_TOO_YOUNG,
        fraud_models.FraudReasonCode.NOT_ELIGIBLE,
    ):
        pop_over_icon = subscription_models.PopOverIcon.ERROR

    elif relevant_reason_code == fraud_models.FraudReasonCode.ID_CHECK_DATA_MATCH:
        call_to_action = subscription_messages.compute_support_call_to_action(fraud_check.user.id)

    else:
        call_to_action = subscription_messages.REDIRECT_TO_DMS_CALL_TO_ACTION

    return subscription_models.SubscriptionMessage(
        user_message=user_message,
        call_to_action=call_to_action,
        pop_over_icon=pop_over_icon,
        updated_at=fraud_check.updatedAt,
    )
