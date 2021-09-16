from pcapi import settings
from pcapi.notifications.push.backends.batch import BatchBackend
from pcapi.notifications.push.backends.batch import UserUpdateData
from pcapi.notifications.push.transactional_notifications import TransactionalNotificationData
from pcapi.utils.module_loading import import_string


def update_user_attributes(user_id: int, attribute_values: dict) -> None:
    backend = import_string(settings.PUSH_NOTIFICATION_BACKEND)
    backend().update_user_attributes(user_id, attribute_values)


def update_user_attributes_with_legacy_internal_task(user_id: int, attribute_values: dict) -> None:
    backend = import_string(settings.PUSH_NOTIFICATION_BACKEND)
    if backend == BatchBackend:
        backend().update_user_attributes_with_legacy_internal_task(user_id, attribute_values)
    else:
        update_user_attributes(user_id, attribute_values)


def update_users_attributes(users_data: list[UserUpdateData]) -> None:
    backend = import_string(settings.PUSH_NOTIFICATION_BACKEND)
    backend().update_users_attributes(users_data)


def send_transactional_notification(notification_data: TransactionalNotificationData) -> None:
    backend = import_string(settings.PUSH_NOTIFICATION_BACKEND)
    backend().send_transactional_notification(notification_data)
