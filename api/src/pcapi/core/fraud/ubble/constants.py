from pcapi.core.fraud import models as fraud_models


RESTARTABLE_FRAUD_CHECK_REASON_CODES = (
    # Reasons which allow user to retry ubble identification
    fraud_models.FraudReasonCode.BLURRY_DOCUMENT_VIDEO,
    fraud_models.FraudReasonCode.BLURRY_VIDEO,
    fraud_models.FraudReasonCode.DOCUMENT_DAMAGED,
    fraud_models.FraudReasonCode.ID_CHECK_BLOCKED_OTHER,
    fraud_models.FraudReasonCode.ID_CHECK_EXPIRED,
    fraud_models.FraudReasonCode.ID_CHECK_NOT_AUTHENTIC,
    fraud_models.FraudReasonCode.ID_CHECK_NOT_SUPPORTED,
    fraud_models.FraudReasonCode.ID_CHECK_UNPROCESSABLE,
    fraud_models.FraudReasonCode.LACK_OF_LUMINOSITY,
    fraud_models.FraudReasonCode.MISSING_REQUIRED_DATA,
    fraud_models.FraudReasonCode.NETWORK_CONNECTION_ISSUE,
)

REASON_CODE_REQUIRING_EMAIL_UPDATE = (
    # Reasons which require an email to user when occuring
    fraud_models.FraudReasonCode.BLURRY_DOCUMENT_VIDEO,
    fraud_models.FraudReasonCode.BLURRY_VIDEO,
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
)

MAX_UBBLE_RETRIES = 3
