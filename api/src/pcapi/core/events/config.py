import enum

from pcapi import settings


class EventName(enum.Enum):
    USER_DEPOSIT_ACTIVATED = "user_deposit_activated"
    USER_IDENTITY_CHECK_STARTED = "user_identity_check_started"
    HAS_UBBLE_KO_STATUS = "has_ubble_ko_status"


EVENTS_DISPATCHING = {
    EventName.USER_DEPOSIT_ACTIVATED: [
        settings.EMAIL_BACKEND,
    ],
}
