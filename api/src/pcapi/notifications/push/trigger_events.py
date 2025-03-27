import enum

from pcapi.routes.serialization import BaseModel


class BatchEvent(enum.Enum):
    RECREDITED_ACCOUNT = "recredited_account"
    USER_DEPOSIT_ACTIVATED = "user_deposit_activated"
    USER_IDENTITY_CHECK_STARTED = "user_identity_check_started"
    HAS_ADDED_OFFER_TO_FAVORITES = "has_added_offer_to_favorites"
    HAS_UBBLE_KO_STATUS = "has_ubble_ko_status"
    HAS_BOOKED_OFFER = "has_booked_offer"
    RECREDIT_ACCOUNT_CANCELLATION = "recredit_account_cancellation"
    FUTURE_OFFER_ACTIVATED = "Future_offer_activated"


class TrackBatchEventRequest(BaseModel):
    user_id: int
    event_name: BatchEvent
    event_payload: dict


class TrackBatchEventsRequest(BaseModel):
    trigger_events: list[TrackBatchEventRequest]
