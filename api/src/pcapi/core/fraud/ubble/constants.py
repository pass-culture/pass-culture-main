from pcapi.core.fraud import models as fraud_models


RESTARTABLE_FRAUD_CHECK_REASON_CODES = (
    # Reasons which allow user to retry ubble identification
    fraud_models.FraudReasonCode.ID_CHECK_NOT_SUPPORTED,
    fraud_models.FraudReasonCode.ID_CHECK_EXPIRED,
    fraud_models.FraudReasonCode.ID_CHECK_UNPROCESSABLE,
)

MAX_UBBLE_RETRIES = 3
