import enum

from pcapi import settings
from pcapi.notifications.push.backends.batch import BatchAPI
from pcapi.notifications.push.backends.batch import UserUpdateData
from pcapi.notifications.push.transactional_notifications import TransactionalNotificationData
from pcapi.utils.module_loading import import_string


class BatchEvent(enum.Enum):
    USER_DEPOSIT_ACTIVATED = "user_deposit_activated"
    USER_IDENTITY_CHECK_STARTED = "user_identity_check_started"
    HAS_ADDED_OFFER_TO_FAVORITES = "has_added_offer_to_favorites"
    HAS_UBBLE_KO_STATUS = "has_ubble_ko_status"


def update_user_attributes(
    batch_api: BatchAPI, user_id: int, attribute_values: dict, can_be_asynchronously_retried: bool = False
) -> None:
    backend = import_string(settings.PUSH_NOTIFICATION_BACKEND)
    return backend().update_user_attributes(
        batch_api, user_id, attribute_values, can_be_asynchronously_retried=can_be_asynchronously_retried
    )


def update_users_attributes(users_data: list[UserUpdateData], can_be_asynchronously_retried: bool = False) -> None:
    backend = import_string(settings.PUSH_NOTIFICATION_BACKEND)
    backend().update_users_attributes(users_data, can_be_asynchronously_retried=can_be_asynchronously_retried)


def send_transactional_notification(
    notification_data: TransactionalNotificationData, can_be_asynchronously_retried: bool = False
) -> None:
    backend = import_string(settings.PUSH_NOTIFICATION_BACKEND)
    backend().send_transactional_notification(
        notification_data, can_be_asynchronously_retried=can_be_asynchronously_retried
    )


def delete_user_attributes(user_id: int, can_be_asynchronously_retried: bool = False) -> None:
    backend = import_string(settings.PUSH_NOTIFICATION_BACKEND)
    backend().delete_user_attributes(user_id, can_be_asynchronously_retried=can_be_asynchronously_retried)


def track_event(
    user_id: int, event: BatchEvent, event_payload: dict, can_be_asynchronously_retried: bool = False
) -> None:
    backend = import_string(settings.PUSH_NOTIFICATION_BACKEND)
    backend().track_event(
        user_id, event.value, event_payload, can_be_asynchronously_retried=can_be_asynchronously_retried
    )
