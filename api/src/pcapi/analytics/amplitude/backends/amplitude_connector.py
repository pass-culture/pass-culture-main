import enum
import logging

import amplitude as amplitude_sdk

from pcapi import settings


AMPLITUDE_API_PUBLIC_KEY = settings.AMPLITUDE_API_PUBLIC_KEY
logger = logging.getLogger(__name__)


class AmplitudeEventType(enum.Enum):
    BOOKING_CANCELLED = "BOOKING_CANCELLED"
    BOOKING_USED = "BOOKING_USED"
    DEPOSIT_GRANTED = "DEPOSIT_GRANTED"
    DMS_ERROR = "DMS_ERROR"
    EDUCONNECT_ERROR = "EDUCONNECT_ERROR"
    OFFER_BOOKED = "OFFER_BOOKED"
    UBBLE_ERROR = "UBBLE_ERROR"


class AmplitudeBackend:
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
        event_name: AmplitudeEventType,
        event_properties: dict | None = None,
    ) -> None:
        event = amplitude_sdk.BaseEvent(
            user_id=str(user_id),
            event_type=event_name.value,
            event_properties=event_properties,
        )
        self.client.track(event)
