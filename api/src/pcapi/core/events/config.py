import enum

from pcapi import settings


class AmplitudeEventType(enum.Enum):
    BOOKING_CANCELLED = "BOOKING_CANCELLED"
    BOOKING_USED = "BOOKING_USED"
    DEPOSIT_GRANTED = "DEPOSIT_GRANTED"
    DMS_ERROR = "DMS_ERROR"
    EDUCONNECT_ERROR = "EDUCONNECT_ERROR"
    OFFER_BOOKED = "OFFER_BOOKED"
    UBBLE_ERROR = "UBBLE_ERROR"


class BatchEvent(enum.Enum):
    USER_DEPOSIT_ACTIVATED = "user_deposit_activated"
    USER_IDENTITY_CHECK_STARTED = "user_identity_check_started"
    HAS_UBBLE_KO_STATUS = "has_ubble_ko_status"


class EventName(enum.Enum):
    # Batch
    USER_DEPOSIT_ACTIVATED = "user_deposit_activated"
    USER_IDENTITY_CHECK_STARTED = "user_identity_check_started"
    HAS_UBBLE_KO_STATUS = "has_ubble_ko_status"

    # Amplitude
    BOOKING_CANCELLED = "BOOKING_CANCELLED"
    BOOKING_USED = "BOOKING_USED"
    DEPOSIT_GRANTED = "DEPOSIT_GRANTED"
    DMS_ERROR = "DMS_ERROR"
    EDUCONNECT_ERROR = "EDUCONNECT_ERROR"
    OFFER_BOOKED = "OFFER_BOOKED"
    UBBLE_ERROR = "UBBLE_ERROR"


EVENTS_DISPATCHING = {
    EventName.USER_DEPOSIT_ACTIVATED: [settings.PUSH_NOTIFICATION_BACKEND],
    EventName.USER_IDENTITY_CHECK_STARTED: [settings.PUSH_NOTIFICATION_BACKEND],
    EventName.HAS_UBBLE_KO_STATUS: [settings.PUSH_NOTIFICATION_BACKEND],
    EventName.BOOKING_CANCELLED: [settings.AMPLITUDE_BACKEND],
    EventName.BOOKING_USED: [settings.AMPLITUDE_BACKEND],
    EventName.DMS_ERROR: [settings.AMPLITUDE_BACKEND],
}


# Legacy events mapping
LEGACY_EVENTS_DISPATCHING = {
    EventName.USER_DEPOSIT_ACTIVATED: [
        {"backend": settings.EMAIL_BACKEND, "event": AmplitudeEventType.DEPOSIT_GRANTED},
        {"backend": settings.PUSH_NOTIFICATION_BACKEND, "event": BatchEvent.USER_DEPOSIT_ACTIVATED},
    ],
}


assert (
    set(EVENTS_DISPATCHING) & set(LEGACY_EVENTS_DISPATCHING) == set()
), f"{set(EVENTS_DISPATCHING) & set(LEGACY_EVENTS_DISPATCHING) = }"
