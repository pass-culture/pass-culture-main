import logging

from pcapi.analytics.amplitude.backends.base import BaseBackend
from pcapi.core.events import Event
from pcapi.core.events.config import EventName


logger = logging.getLogger(__name__)


class LoggerBackend(BaseBackend):
    def track_event(
        self,
        user_id: int,
        event_name: EventName,
        event_properties: dict | None = None,
    ) -> None:
        logger.info(
            "A request to track Amplitude event=%s would be sent for user with id=%d",
            event_name.value,
            user_id,
            extra=event_properties,
        )

    def handle_event(self, event: Event) -> None:
        return super().handle_event(event)
