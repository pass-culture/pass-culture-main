from pcapi.core.fraud import models as fraud_models


RESTARTABLE_FRAUD_CHECK_REASON_CODES = (
    # Reasons which allow user to retry ubble identification
    fraud_models.FraudReasonCode.BLURRY_DOCUMENT_VIDEO,
    fraud_models.FraudReasonCode.DOCUMENT_DAMAGED,
    fraud_models.FraudReasonCode.ID_CHECK_BLOCKED_OTHER,
    fraud_models.FraudReasonCode.ID_CHECK_EXPIRED,
    fraud_models.FraudReasonCode.ID_CHECK_NOT_AUTHENTIC,
    fraud_models.FraudReasonCode.ID_CHECK_NOT_SUPPORTED,
    fraud_models.FraudReasonCode.ID_CHECK_UNPROCESSABLE,
    fraud_models.FraudReasonCode.LACK_OF_LUMINOSITY,
    fraud_models.FraudReasonCode.MISSING_REQUIRED_DATA,
    fraud_models.FraudReasonCode.NETWORK_CONNECTION_ISSUE,
    fraud_models.FraudReasonCode.NOT_DOCUMENT_OWNER,
    fraud_models.FraudReasonCode.UBBLE_INTERNAL_ERROR,
)

REASON_CODE_REQUIRING_IMMEDIATE_EMAIL_REMINDER = (
    fraud_models.FraudReasonCode.BLURRY_DOCUMENT_VIDEO,
    fraud_models.FraudReasonCode.DOCUMENT_DAMAGED,
    fraud_models.FraudReasonCode.ID_CHECK_BLOCKED_OTHER,
    fraud_models.FraudReasonCode.ID_CHECK_DATA_MATCH,
    fraud_models.FraudReasonCode.ID_CHECK_EXPIRED,
    fraud_models.FraudReasonCode.ID_CHECK_NOT_AUTHENTIC,
    fraud_models.FraudReasonCode.ID_CHECK_NOT_SUPPORTED,
    fraud_models.FraudReasonCode.ID_CHECK_UNPROCESSABLE,
    fraud_models.FraudReasonCode.LACK_OF_LUMINOSITY,
    fraud_models.FraudReasonCode.MISSING_REQUIRED_DATA,
    fraud_models.FraudReasonCode.NETWORK_CONNECTION_ISSUE,
    fraud_models.FraudReasonCode.NOT_DOCUMENT_OWNER,
    fraud_models.FraudReasonCode.UBBLE_INTERNAL_ERROR,
)

REASON_CODE_REQUIRING_IMMEDIATE_NOTIFICATION_REMINDER = (
    fraud_models.FraudReasonCode.BLURRY_DOCUMENT_VIDEO,
    fraud_models.FraudReasonCode.DOCUMENT_DAMAGED,
    fraud_models.FraudReasonCode.ID_CHECK_BLOCKED_OTHER,
    fraud_models.FraudReasonCode.ID_CHECK_EXPIRED,
    fraud_models.FraudReasonCode.ID_CHECK_NOT_AUTHENTIC,
    fraud_models.FraudReasonCode.ID_CHECK_NOT_SUPPORTED,
    fraud_models.FraudReasonCode.ID_CHECK_UNPROCESSABLE,
    fraud_models.FraudReasonCode.LACK_OF_LUMINOSITY,
    fraud_models.FraudReasonCode.MISSING_REQUIRED_DATA,
    fraud_models.FraudReasonCode.NETWORK_CONNECTION_ISSUE,
    fraud_models.FraudReasonCode.NOT_DOCUMENT_OWNER,
    fraud_models.FraudReasonCode.UBBLE_INTERNAL_ERROR,
)

REASON_CODES_FOR_QUICK_ACTION_REMINDERS = (
    fraud_models.FraudReasonCode.BLURRY_DOCUMENT_VIDEO,
    fraud_models.FraudReasonCode.DOCUMENT_DAMAGED,
    fraud_models.FraudReasonCode.ID_CHECK_BLOCKED_OTHER,
    fraud_models.FraudReasonCode.ID_CHECK_NOT_AUTHENTIC,
    fraud_models.FraudReasonCode.ID_CHECK_UNPROCESSABLE,
    fraud_models.FraudReasonCode.LACK_OF_LUMINOSITY,
    fraud_models.FraudReasonCode.MISSING_REQUIRED_DATA,
    fraud_models.FraudReasonCode.NETWORK_CONNECTION_ISSUE,
    fraud_models.FraudReasonCode.NOT_DOCUMENT_OWNER,
    fraud_models.FraudReasonCode.UBBLE_INTERNAL_ERROR,
)

REASON_CODES_FOR_LONG_ACTION_REMINDERS = (
    fraud_models.FraudReasonCode.ID_CHECK_EXPIRED,
    fraud_models.FraudReasonCode.ID_CHECK_NOT_SUPPORTED,
)

MAX_UBBLE_RETRIES = 3
