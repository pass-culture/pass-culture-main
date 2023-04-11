import logging

from pcapi.analytics.amplitude.backends.amplitude_connector import AmplitudeEventType
from pcapi.core.finance import models as finance_models
from pcapi.core.fraud import models as fraud_models
from pcapi.tasks import amplitude_tasks


logger = logging.getLogger(__name__)


def track_deposit_activation_event(
    user_id: int, deposit: finance_models.Deposit, fraud_check: fraud_models.BeneficiaryFraudCheck
) -> None:
    amplitude_tasks.track_event.delay(
        amplitude_tasks.TrackAmplitudeEventRequest(
            user_id=user_id,
            event_name=AmplitudeEventType.DEPOSIT_GRANTED,
            event_properties={"from": fraud_check.type.value},
        )
    )


def track_educonnect_error_event(user_id: int, error_codes: list[fraud_models.FraudReasonCode]) -> None:
    _track_identity_check_error_event(user_id, error_codes, fraud_models.FraudCheckType.EDUCONNECT)


def track_ubble_error_event(user_id: int, error_codes: list[fraud_models.FraudReasonCode]) -> None:
    _track_identity_check_error_event(user_id, error_codes, fraud_models.FraudCheckType.UBBLE)


def track_dms_error_event(
    user_id: int,
    error_codes: list[fraud_models.FraudReasonCode],
    field_errors: list[fraud_models.DmsFieldErrorDetails] = None,
) -> None:
    event_properties = (
        {"field_errors": [{"key": field_error.key.value, "value": field_error.value} for field_error in field_errors]}
        if field_errors
        else None
    )
    _track_identity_check_error_event(
        user_id, error_codes, fraud_models.FraudCheckType.DMS, event_properties=event_properties
    )


def _track_identity_check_error_event(
    user_id: int,
    error_codes: list[fraud_models.FraudReasonCode],
    fraud_check_type: fraud_models.FraudCheckType,
    event_properties: dict | None = None,
) -> None:
    match fraud_check_type:
        case fraud_models.FraudCheckType.EDUCONNECT:
            event_name = AmplitudeEventType.EDUCONNECT_ERROR
        case fraud_models.FraudCheckType.UBBLE:
            event_name = AmplitudeEventType.UBBLE_ERROR
        case fraud_models.FraudCheckType.DMS:
            event_name = AmplitudeEventType.DMS_ERROR
        case _:
            logger.warning("Unknown fraud check type: %s", fraud_check_type)
            return

    if event_properties is None:
        event_properties = {}

    event_properties |= {"error_codes": [error_codes.value for error_codes in error_codes]}

    amplitude_tasks.track_event.delay(
        amplitude_tasks.TrackAmplitudeEventRequest(
            user_id=user_id, event_name=event_name, event_properties=event_properties
        )
    )
