import logging

from pcapi.analytics.amplitude.backends.amplitude_connector import AmplitudeEventType


logger = logging.getLogger(__name__)


class LoggerBackend:
    def track_event(
        self,
        user_id: int,
        event_name: AmplitudeEventType,
        event_properties: dict | None = None,
    ) -> None:
        logger.info(
            "A request to track Amplitude event=%s would be sent for user with id=%d",
            event_name,
            user_id,
            extra=event_properties,
        )
