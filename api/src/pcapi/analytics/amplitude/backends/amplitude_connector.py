import logging

import amplitude as amplitude_sdk

from pcapi import settings
from pcapi.core.events import Event
from pcapi.core.events.backend import ExternalServiceBackend
from pcapi.core.events.config import EventName

AMPLITUDE_API_PUBLIC_KEY = settings.AMPLITUDE_API_PUBLIC_KEY
logger = logging.getLogger(__name__)


class AmplitudeBackend(ExternalServiceBackend):
    client: amplitude_sdk.Amplitude

    def __init__(self) -> None:
        client = amplitude_sdk.Amplitude(AMPLITUDE_API_PUBLIC_KEY)
        client.configuration.logger = logger
        client.configuration.min_id_length = 1
        client.configuration.server_zone = "EU"
        client.configuration.use_batch = True
        client.configuration.opt_out = False

        self.client = client

    def track_event(
        self,
        user_id: int,
        event_name: EventName,
        event_properties: dict | None = None,
    ) -> None:
        event = amplitude_sdk.BaseEvent(
            user_id=str(user_id),
            event_type=event_name.value,
            event_properties=event_properties,
        )
        self.client.track(event)

    def handle_event(self, event: Event) -> None:
        self.track_event(event.user_ids[0], event.name, event.payload)
