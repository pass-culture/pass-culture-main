from pcapi.notifications.push import models as push_models
from pcapi.notifications.push import testing
from pcapi.notifications.push.backends.batch import BatchAPI
from pcapi.notifications.push.backends.batch import UserUpdateData
from pcapi.notifications.push.backends.logger import LoggerBackend
from pcapi.notifications.push.transactional_notifications import TransactionalNotificationData


class TestingBackend(LoggerBackend):
    def update_user_attributes(
        self, batch_api: BatchAPI, user_id: int, attribute_values: dict
    ) -> push_models.UpdateAttributeRequestResult:
        super().update_user_attributes(batch_api, user_id, attribute_values)
        testing.requests.append({"user_id": user_id, "attribute_values": attribute_values, "batch_api": batch_api.name})
        return push_models.UpdateAttributeRequestResult(should_retry=False)

    def update_users_attributes(self, users_data: list[UserUpdateData]) -> None:
        super().update_users_attributes(users_data)
        testing.requests.append(users_data)

    def send_transactional_notification(self, notification_data: TransactionalNotificationData) -> None:
        super().send_transactional_notification(notification_data)
        testing.requests.append(
            {
                "group_id": notification_data.group_id,
                "user_ids": notification_data.user_ids,
                "message": {"title": notification_data.message.title, "body": notification_data.message.body},
                **notification_data.extra,  # type: ignore [arg-type]
            }
        )

    def delete_user_attributes(self, user_id: int) -> None:
        super().delete_user_attributes(user_id)
        testing.requests.append({"user_id": user_id})
