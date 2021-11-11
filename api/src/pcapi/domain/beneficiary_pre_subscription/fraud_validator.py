import dataclasses
import logging

from pcapi.core.subscription.models import BeneficiaryPreSubscription
from pcapi.domain.beneficiary_pre_subscription.exceptions import FraudDetected
from pcapi.domain.beneficiary_pre_subscription.exceptions import SuspiciousFraudDetected


logger = logging.getLogger(__name__)


def validate_fraud(beneficiary_pre_subscription: BeneficiaryPreSubscription) -> None:
    strict_controls = beneficiary_pre_subscription.fraud_fields["strict_controls"]
    non_blocking_controls = beneficiary_pre_subscription.fraud_fields["non_blocking_controls"]

    fraud_detected = any(not item.valid for item in strict_controls)
    suspicious_fraud_detected = any(not item.valid for item in non_blocking_controls)

    if fraud_detected or suspicious_fraud_detected:
        controls = strict_controls + non_blocking_controls
        ok_controls = [item for item in controls if item.valid]
        ko_controls = [item for item in controls if not item.valid]

        extra_log = {
            "email": beneficiary_pre_subscription.email,
            "applicationId": beneficiary_pre_subscription.application_id,
            "okControls": [dataclasses.asdict(control) for control in ok_controls],
            "koControls": [dataclasses.asdict(control) for control in ko_controls],
        }

        if fraud_detected:
            logger.warning("Id check STRICT fraud control ko", extra=extra_log)
            error_msg = ", ".join([control.key for control in ko_controls])
            raise FraudDetected(error_msg)

        if suspicious_fraud_detected:
            logger.warning("Id check SOFT fraud control ko", extra=extra_log)
            error_msg = ", ".join([control.key for control in controls])
            raise SuspiciousFraudDetected(error_msg)
