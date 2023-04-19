import enum
from typing import TYPE_CHECKING
from pcapi.core.events import Event
from pcapi.core.events.backend import ExternalServiceBackend

if TYPE_CHECKING:
    from pcapi.core.events.config import EventName


class BaseBackend(ExternalServiceBackend):
    def track_event(
        self,
        user_id: int,
        event_name: "EventName",
        event_properties: dict | None = None,
    ) -> None:
        raise NotImplementedError()

    def handle_event(self, event: Event) -> None:
        return super().handle_event(event)
