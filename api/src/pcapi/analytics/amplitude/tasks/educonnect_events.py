from pcapi.analytics.amplitude.backends.amplitude_connector import AmplitudeEventType
from pcapi.core.fraud import models as fraud_models
from pcapi.tasks import amplitude_tasks


def track_educonnect_error_event(user_id: int, error_codes: list[fraud_models.FraudReasonCode]) -> None:
    amplitude_tasks.track_event.delay(
        amplitude_tasks.TrackAmplitudeEventRequest(
            user_id=user_id,
            event_name=AmplitudeEventType.EDUCONNECT_ERROR,
            event_properties={"error_codes": [error_codes.value for error_codes in error_codes]},
        )
    )
