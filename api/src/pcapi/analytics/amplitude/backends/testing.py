from pcapi.analytics.amplitude import testing
from pcapi.analytics.amplitude.backends.amplitude_connector import AmplitudeEventType
from pcapi.analytics.amplitude.backends.logger import LoggerBackend


class TestingBackend(LoggerBackend):
    def track_event(
        self,
        user_id: int,
        event_name: AmplitudeEventType,
        event_properties: dict | None = None,
    ) -> None:
        super().track_event(user_id, event_name)
        result = {
            "user_id": user_id,
            "event_name": event_name.value,
            "event_properties": event_properties,
        }
        testing.requests.append(result)
