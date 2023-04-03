import logging

from pcapi.analytics.amplitude.backends.amplitude_connector import AmplitudeEventType
from pcapi.core.finance import models as finance_models
from pcapi.core.fraud import models as fraud_models
from pcapi.tasks import amplitude_tasks


logger = logging.getLogger(__name__)


def track_deposit_granted_event(
    user_id: int, deposit: finance_models.Deposit, fraud_check: fraud_models.BeneficiaryFraudCheck
) -> None:
    _track_deposit_activation_event(
        user_id, AmplitudeEventType.DEPOSIT_GRANTED, {"from": fraud_check.type, "source": deposit.source}
    )


def _track_deposit_activation_event(
    user_id: int,
    event_name: AmplitudeEventType,
    event_properties: dict | None = None,
) -> None:
    if event_properties is None:
        event_properties = {}

    amplitude_tasks.track_event.delay(
        amplitude_tasks.TrackAmplitudeEventRequest(
            user_id=user_id, event_name=event_name, event_properties=event_properties
        )
    )
