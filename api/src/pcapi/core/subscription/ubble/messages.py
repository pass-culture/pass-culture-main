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
    if fraud_models.FraudReasonCode.ID_CHECK_UNPROCESSABLE in reason_codes:
        user_message = models.UbbleRetryableUserMessage.ID_CHECK_UNPROCESSABLE.value
        message_summary = models.UbbleRetryableMessageSummary.ID_CHECK_UNPROCESSABLE.value
        action_hint = models.UbbleRetryableActionHint.ID_CHECK_UNPROCESSABLE.value
    elif fraud_models.FraudReasonCode.ID_CHECK_NOT_AUTHENTIC in reason_codes:
        user_message = models.UbbleRetryableUserMessage.ID_CHECK_NOT_AUTHENTIC.value
        message_summary = models.UbbleRetryableMessageSummary.ID_CHECK_NOT_AUTHENTIC.value
        action_hint = models.UbbleRetryableActionHint.ID_CHECK_NOT_AUTHENTIC.value
    elif fraud_models.FraudReasonCode.ID_CHECK_NOT_SUPPORTED in reason_codes:
        user_message = models.UbbleRetryableUserMessage.ID_CHECK_NOT_SUPPORTED.value
        message_summary = models.UbbleRetryableMessageSummary.ID_CHECK_NOT_SUPPORTED.value
        action_hint = models.UbbleRetryableActionHint.ID_CHECK_NOT_SUPPORTED.value
    elif fraud_models.FraudReasonCode.ID_CHECK_EXPIRED in reason_codes:
        user_message = models.UbbleRetryableUserMessage.ID_CHECK_EXPIRED.value
        message_summary = models.UbbleRetryableMessageSummary.ID_CHECK_EXPIRED.value
        action_hint = models.UbbleRetryableActionHint.ID_CHECK_EXPIRED.value
    elif fraud_models.FraudReasonCode.BLURRY_VIDEO in reason_codes:
        user_message = models.UbbleRetryableUserMessage.BLURRY_VIDEO.value
        message_summary = models.UbbleRetryableMessageSummary.BLURRY_VIDEO.value
        action_hint = models.UbbleRetryableActionHint.BLURRY_VIDEO.value
    elif fraud_models.FraudReasonCode.NETWORK_CONNECTION_ISSUE in reason_codes:
        user_message = models.UbbleRetryableUserMessage.NETWORK_CONNECTION_ISSUE.value
        message_summary = models.UbbleRetryableMessageSummary.NETWORK_CONNECTION_ISSUE.value
        action_hint = models.UbbleRetryableActionHint.NETWORK_CONNECTION_ISSUE.value
    elif fraud_models.FraudReasonCode.LACK_OF_LUMINOSITY in reason_codes:
        user_message = models.UbbleRetryableUserMessage.LACK_OF_LUMINOSITY.value
        message_summary = models.UbbleRetryableMessageSummary.LACK_OF_LUMINOSITY.value
        action_hint = models.UbbleRetryableActionHint.LACK_OF_LUMINOSITY.value
    elif fraud_models.FraudReasonCode.DOCUMENT_DAMAGED in reason_codes:
        user_message = models.UbbleRetryableUserMessage.DOCUMENT_DAMAGED.value
        message_summary = models.UbbleRetryableMessageSummary.DOCUMENT_DAMAGED.value
        action_hint = models.UbbleRetryableActionHint.DOCUMENT_DAMAGED.value
    else:
        user_message = models.UbbleRetryableUserMessage.DEFAULT.value
        message_summary = models.UbbleRetryableMessageSummary.DEFAULT.value
        action_hint = models.UbbleRetryableActionHint.DEFAULT.value

    return subscription_models.SubscriptionMessage(
        user_message=user_message,
        message_summary=message_summary,
        action_hint=action_hint,
        call_to_action=subscription_messages.REDIRECT_TO_IDENTIFICATION_CHOICE,
        pop_over_icon=None,
        updated_at=updated_at,
    )


def get_ubble_not_retryable_message(
    fraud_check: fraud_models.BeneficiaryFraudCheck,
) -> subscription_models.SubscriptionMessage:
    reason_codes = fraud_check.reasonCodes or []
    if fraud_check.resultContent:
        identity_content = typing.cast(common_fraud_models.IdentityCheckContent, fraud_check.source_data())
    else:
        identity_content = None

    call_to_action = None
    pop_over_icon = None
    if fraud_models.FraudReasonCode.ID_CHECK_UNPROCESSABLE in reason_codes:
        user_message = models.UbbleNotRetryableUserMessage.ID_CHECK_UNPROCESSABLE.value
        call_to_action = subscription_messages.REDIRECT_TO_DMS_CALL_TO_ACTION

    elif fraud_models.FraudReasonCode.ID_CHECK_NOT_AUTHENTIC in reason_codes:
        user_message = models.UbbleNotRetryableUserMessage.ID_CHECK_NOT_AUTHENTIC.value
        call_to_action = subscription_messages.REDIRECT_TO_DMS_CALL_TO_ACTION

    elif fraud_models.FraudReasonCode.ID_CHECK_NOT_SUPPORTED in reason_codes:
        user_message = models.UbbleNotRetryableUserMessage.ID_CHECK_NOT_SUPPORTED.value
        call_to_action = subscription_messages.REDIRECT_TO_DMS_CALL_TO_ACTION

    elif fraud_models.FraudReasonCode.ID_CHECK_EXPIRED in reason_codes:
        user_message = models.UbbleNotRetryableUserMessage.ID_CHECK_EXPIRED.value
        call_to_action = subscription_messages.REDIRECT_TO_DMS_CALL_TO_ACTION

    elif fraud_models.FraudReasonCode.DUPLICATE_USER in reason_codes:
        user_message = subscription_messages.build_duplicate_error_message(
            fraud_check.user, fraud_models.FraudReasonCode.DUPLICATE_USER, identity_content
        )
        call_to_action = subscription_messages.compute_support_call_to_action(fraud_check.user.id)

    elif fraud_models.FraudReasonCode.DUPLICATE_ID_PIECE_NUMBER in reason_codes:
        user_message = subscription_messages.build_duplicate_error_message(
            fraud_check.user, fraud_models.FraudReasonCode.DUPLICATE_ID_PIECE_NUMBER, identity_content
        )
        call_to_action = subscription_messages.compute_support_call_to_action(fraud_check.user.id)

    elif fraud_models.FraudReasonCode.AGE_TOO_YOUNG in reason_codes:
        user_message = models.UbbleNotRetryableUserMessage.AGE_TOO_YOUNG.value
        pop_over_icon = subscription_models.PopOverIcon.ERROR

    elif fraud_models.FraudReasonCode.AGE_TOO_OLD in reason_codes:
        user_message = models.UbbleNotRetryableUserMessage.AGE_TOO_OLD.value
        pop_over_icon = subscription_models.PopOverIcon.ERROR

    elif fraud_models.FraudReasonCode.NOT_ELIGIBLE in reason_codes:
        user_message = models.UbbleNotRetryableUserMessage.NOT_ELIGIBLE.value
        pop_over_icon = subscription_models.PopOverIcon.ERROR

    elif fraud_models.FraudReasonCode.ID_CHECK_DATA_MATCH in reason_codes:
        user_message = models.UbbleNotRetryableUserMessage.ID_CHECK_DATA_MATCH.value
        call_to_action = subscription_messages.compute_support_call_to_action(fraud_check.user.id)

    elif fraud_models.FraudReasonCode.BLURRY_VIDEO in reason_codes:
        user_message = models.UbbleNotRetryableUserMessage.BLURRY_VIDEO.value
        call_to_action = subscription_messages.REDIRECT_TO_DMS_CALL_TO_ACTION

    elif fraud_models.FraudReasonCode.NETWORK_CONNECTION_ISSUE in reason_codes:
        user_message = models.UbbleNotRetryableUserMessage.NETWORK_CONNECTION_ISSUE.value
        call_to_action = subscription_messages.REDIRECT_TO_DMS_CALL_TO_ACTION

    elif fraud_models.FraudReasonCode.LACK_OF_LUMINOSITY in reason_codes:
        user_message = models.UbbleNotRetryableUserMessage.LACK_OF_LUMINOSITY.value
        call_to_action = subscription_messages.REDIRECT_TO_DMS_CALL_TO_ACTION

    elif fraud_models.FraudReasonCode.DOCUMENT_DAMAGED in reason_codes:
        user_message = models.UbbleNotRetryableUserMessage.DOCUMENT_DAMAGED.value
        call_to_action = subscription_messages.REDIRECT_TO_DMS_CALL_TO_ACTION

    elif fraud_models.FraudReasonCode.ID_CHECK_BLOCKED_OTHER in reason_codes:
        user_message = models.UbbleNotRetryableUserMessage.ID_CHECK_BLOCKED_OTHER.value
        call_to_action = subscription_messages.REDIRECT_TO_DMS_CALL_TO_ACTION

    else:
        user_message = models.UbbleNotRetryableUserMessage.DEFAULT.value
        call_to_action = subscription_messages.REDIRECT_TO_DMS_CALL_TO_ACTION

    return subscription_models.SubscriptionMessage(
        user_message=user_message,
        call_to_action=call_to_action,
        pop_over_icon=pop_over_icon,
        updated_at=fraud_check.updatedAt,
    )
