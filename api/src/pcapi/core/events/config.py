import enum
from typing import Any

from pcapi import settings


import pcapi.core.finance.models as finance_models
import pcapi.core.fraud.models as fraud_models


class EventName(enum.Enum):
    USER_DEPOSIT_ACTIVATED = "user_deposit_activated"
    USER_IDENTITY_CHECK_STARTED = "user_identity_check_started"
    HAS_UBBLE_KO_STATUS = "has_ubble_ko_status"
    BOOKING_CANCELLED = "BOOKING_CANCELLED"
    BOOKING_USED = "BOOKING_USED"
    DMS_ERROR = "DMS_ERROR"
    EDUCONNECT_ERROR = "EDUCONNECT_ERROR"
    OFFER_BOOKED = "OFFER_BOOKED"
    UBBLE_ERROR = "UBBLE_ERROR"


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


EVENTS_DISPATCHING: dict[EventName, dict[str, Any]] = {
    EventName.USER_DEPOSIT_ACTIVATED: {
        "services": [settings.AMPLITUDE_BACKEND, settings.PUSH_NOTIFICATION_BACKEND],
        "properties": {"deposit": finance_models.Deposit, "fraud_check_type": fraud_models.FraudCheckType},
    },
    EventName.USER_IDENTITY_CHECK_STARTED: {
        "services": [settings.PUSH_NOTIFICATION_BACKEND],
        "properties": {},
    },
    EventName.HAS_UBBLE_KO_STATUS: {
        "services": [settings.PUSH_NOTIFICATION_BACKEND],
        "properties": {},
    },
    EventName.BOOKING_CANCELLED: {
        "services": [settings.AMPLITUDE_BACKEND],
        "properties": {},
    },
    EventName.BOOKING_USED: {
        "services": [settings.AMPLITUDE_BACKEND],
        "properties": {},
    },
    EventName.DMS_ERROR: {
        "services": [settings.AMPLITUDE_BACKEND],
        "properties": {},
    },
    EventName.EDUCONNECT_ERROR: {
        "services": [settings.AMPLITUDE_BACKEND],
        "properties": {},
    },
    EventName.OFFER_BOOKED: {
        "services": [settings.AMPLITUDE_BACKEND],
        "properties": {},
    },
    EventName.UBBLE_ERROR: {
        "services": [settings.AMPLITUDE_BACKEND],
        "properties": {},
    },
}

LEGACY_EVENTS_TRANSLATION = {
    EventName.USER_DEPOSIT_ACTIVATED: {
        settings.AMPLITUDE_BACKEND: AmplitudeEventType.DEPOSIT_GRANTED,
        settings.PUSH_NOTIFICATION_BACKEND: BatchEvent.USER_DEPOSIT_ACTIVATED,
    }
}


assert (
    len([event_name for event_name in EventName if event_name not in EVENTS_DISPATCHING]) == 0
), f"{[event_name for event_name in EventName if event_name not in EVENTS_DISPATCHING], = }"
