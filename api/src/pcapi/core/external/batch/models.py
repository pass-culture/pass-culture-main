import enum


class BatchEvent(enum.Enum):
    RECREDITED_ACCOUNT = "recredited_account"
    USER_DEPOSIT_ACTIVATED = "user_deposit_activated"
    USER_IDENTITY_CHECK_STARTED = "user_identity_check_started"
    HAS_ADDED_OFFER_TO_FAVORITES = "has_added_offer_to_favorites"
    HAS_UBBLE_KO_STATUS = "has_ubble_ko_status"
    HAS_BOOKED_OFFER = "has_booked_offer"
    HAS_RECEIVED_BONUS = "has_received_bonus"
    RECREDIT_ACCOUNT_CANCELLATION = "recredit_account_cancellation"
    FUTURE_OFFER_ACTIVATED = "future_offer_activated"
