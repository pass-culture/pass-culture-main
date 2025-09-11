from pcapi.core.subscription import models as subscription_models


RESTARTABLE_FRAUD_CHECK_REASON_CODES = (
    # Reasons which allow user to retry ubble identification
    subscription_models.FraudReasonCode.BLURRY_DOCUMENT_VIDEO,
    subscription_models.FraudReasonCode.DOCUMENT_DAMAGED,
    subscription_models.FraudReasonCode.ID_CHECK_BLOCKED_OTHER,
    subscription_models.FraudReasonCode.ID_CHECK_EXPIRED,
    subscription_models.FraudReasonCode.ID_CHECK_NOT_AUTHENTIC,
    subscription_models.FraudReasonCode.ID_CHECK_NOT_SUPPORTED,
    subscription_models.FraudReasonCode.ID_CHECK_UNPROCESSABLE,
    subscription_models.FraudReasonCode.LACK_OF_LUMINOSITY,
    subscription_models.FraudReasonCode.MISSING_REQUIRED_DATA,
    subscription_models.FraudReasonCode.NETWORK_CONNECTION_ISSUE,
    subscription_models.FraudReasonCode.NOT_DOCUMENT_OWNER,
    subscription_models.FraudReasonCode.UBBLE_INTERNAL_ERROR,
)

REASON_CODE_REQUIRING_IMMEDIATE_EMAIL_REMINDER = (
    subscription_models.FraudReasonCode.BLURRY_DOCUMENT_VIDEO,
    subscription_models.FraudReasonCode.DOCUMENT_DAMAGED,
    subscription_models.FraudReasonCode.ID_CHECK_BLOCKED_OTHER,
    subscription_models.FraudReasonCode.ID_CHECK_DATA_MATCH,
    subscription_models.FraudReasonCode.ID_CHECK_EXPIRED,
    subscription_models.FraudReasonCode.ID_CHECK_NOT_AUTHENTIC,
    subscription_models.FraudReasonCode.ID_CHECK_NOT_SUPPORTED,
    subscription_models.FraudReasonCode.ID_CHECK_UNPROCESSABLE,
    subscription_models.FraudReasonCode.LACK_OF_LUMINOSITY,
    subscription_models.FraudReasonCode.MISSING_REQUIRED_DATA,
    subscription_models.FraudReasonCode.NETWORK_CONNECTION_ISSUE,
    subscription_models.FraudReasonCode.NOT_DOCUMENT_OWNER,
    subscription_models.FraudReasonCode.UBBLE_INTERNAL_ERROR,
)

REASON_CODE_REQUIRING_IMMEDIATE_NOTIFICATION_REMINDER = (
    subscription_models.FraudReasonCode.BLURRY_DOCUMENT_VIDEO,
    subscription_models.FraudReasonCode.DOCUMENT_DAMAGED,
    subscription_models.FraudReasonCode.ID_CHECK_BLOCKED_OTHER,
    subscription_models.FraudReasonCode.ID_CHECK_EXPIRED,
    subscription_models.FraudReasonCode.ID_CHECK_NOT_AUTHENTIC,
    subscription_models.FraudReasonCode.ID_CHECK_NOT_SUPPORTED,
    subscription_models.FraudReasonCode.ID_CHECK_UNPROCESSABLE,
    subscription_models.FraudReasonCode.LACK_OF_LUMINOSITY,
    subscription_models.FraudReasonCode.MISSING_REQUIRED_DATA,
    subscription_models.FraudReasonCode.NETWORK_CONNECTION_ISSUE,
    subscription_models.FraudReasonCode.NOT_DOCUMENT_OWNER,
    subscription_models.FraudReasonCode.UBBLE_INTERNAL_ERROR,
)

REASON_CODES_FOR_QUICK_ACTION_REMINDERS = (
    subscription_models.FraudReasonCode.BLURRY_DOCUMENT_VIDEO,
    subscription_models.FraudReasonCode.DOCUMENT_DAMAGED,
    subscription_models.FraudReasonCode.ID_CHECK_BLOCKED_OTHER,
    subscription_models.FraudReasonCode.ID_CHECK_NOT_AUTHENTIC,
    subscription_models.FraudReasonCode.ID_CHECK_UNPROCESSABLE,
    subscription_models.FraudReasonCode.LACK_OF_LUMINOSITY,
    subscription_models.FraudReasonCode.MISSING_REQUIRED_DATA,
    subscription_models.FraudReasonCode.NETWORK_CONNECTION_ISSUE,
    subscription_models.FraudReasonCode.NOT_DOCUMENT_OWNER,
    subscription_models.FraudReasonCode.UBBLE_INTERNAL_ERROR,
)

REASON_CODES_FOR_LONG_ACTION_REMINDERS = (
    subscription_models.FraudReasonCode.ID_CHECK_EXPIRED,
    subscription_models.FraudReasonCode.ID_CHECK_NOT_SUPPORTED,
)

MAX_UBBLE_RETRIES = 3
