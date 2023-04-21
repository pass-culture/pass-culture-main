from typing import TYPE_CHECKING

from pcapi.core.events import Event
from pcapi.core.events.backend import ExternalServiceBackend


if TYPE_CHECKING:
    from pcapi.core.events.config import EventName


class BaseBackend(ExternalServiceBackend):
    def track_event(
        self, user_id: int, event_name: str, event_payload: dict, can_be_asynchronously_retried: bool = False
    ) -> None:
        raise NotImplementedError()

    def bulk_track_events(
        self, user_ids: list[int], event_name: str, event_payload: dict, can_be_asynchronously_retried: bool = False
    ) -> None:
        raise NotImplementedError()

    def handle_event(self, event: Event) -> None:
        raise NotImplementedError()
