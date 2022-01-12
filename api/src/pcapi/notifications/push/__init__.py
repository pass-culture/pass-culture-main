from pcapi import settings
from pcapi.notifications.push import models as push_models
from pcapi.notifications.push.backends.batch import BatchAPI
from pcapi.notifications.push.backends.batch import UserUpdateData
from pcapi.notifications.push.transactional_notifications import TransactionalNotificationData
from pcapi.utils.module_loading import import_string


def update_user_attributes(
    batch_api: BatchAPI, user_id: int, attribute_values: dict
) -> push_models.UpdateAttributeRequestResult:
    backend = import_string(settings.PUSH_NOTIFICATION_BACKEND)
    return backend().update_user_attributes(batch_api, user_id, attribute_values)


def update_users_attributes(users_data: list[UserUpdateData]) -> None:
    backend = import_string(settings.PUSH_NOTIFICATION_BACKEND)
    backend().update_users_attributes(users_data)


def send_transactional_notification(notification_data: TransactionalNotificationData) -> None:
    backend = import_string(settings.PUSH_NOTIFICATION_BACKEND)
    backend().send_transactional_notification(notification_data)


def delete_user_attributes(user_id: int) -> None:
    backend = import_string(settings.PUSH_NOTIFICATION_BACKEND)
    backend().delete_user_attributes(user_id)
