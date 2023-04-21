from pcapi.core.events import Event
from pcapi.core.events.backend import ExternalServiceBackend


class BaseBackend(ExternalServiceBackend):
    def track_event(
        self,
        user_id: int,
        event_name: str,
        event_properties: dict | None = None,
    ) -> None:
        raise NotImplementedError()

    def handle_event(self, event: Event) -> None:
        name = event.name.value
        if event.legacy_name:
            name = event.legacy_name

        self.track_event(event.user_ids[0], name, event.payload)
