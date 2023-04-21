import logging

from pcapi.analytics.amplitude.backends.base import BaseBackend
from pcapi.core.events import Event


logger = logging.getLogger(__name__)


class LoggerBackend(BaseBackend):
    def track_event(
        self,
        user_id: int,
        event_name: str,
        event_properties: dict | None = None,
    ) -> None:
        logger.info(
            "A request to track Amplitude event=%s would be sent for user with id=%d",
            event_name,
            user_id,
            extra=event_properties,
        )

    def handle_event(self, event: Event) -> None:
        name = event.name.value
        if event.legacy_name:
            name = event.legacy_name
        self.track_event(event.user_ids[0], name, event.payload)
