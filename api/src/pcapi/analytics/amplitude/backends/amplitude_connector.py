import enum
import logging

import amplitude as amplitude_sdk

from pcapi import settings


AMPLITUDE_API_PUBLIC_KEY = settings.AMPLITUDE_API_PUBLIC_KEY


class AmplitudeEventType(enum.Enum):
    EDUCONNECT_ERROR = "Educonnect Error"


class AmplitudeBackend:
    client: amplitude_sdk.Amplitude

    def __init__(self) -> None:
        client = amplitude_sdk.Amplitude(AMPLITUDE_API_PUBLIC_KEY)
        client.configuration.logger = logging.getLogger(__name__)
        client.configuration.min_id_length = 1
        client.configuration.server_zone = "EU"
        client.configuration.use_batch = True
        client.configuration.opt_out = False

        self.client = client

    def track_event(
        self,
        user_id: int,
        event_name: AmplitudeEventType,
        event_properties: dict | None = None,
    ) -> None:
        event = amplitude_sdk.BaseEvent(
            user_id=user_id,
            event_type=event_name.value,
            event_properties=event_properties,
        )
        self.client.track(event)
