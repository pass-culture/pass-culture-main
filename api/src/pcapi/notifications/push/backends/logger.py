import logging

from pcapi.notifications.push.backends.batch import BatchAPI
from pcapi.notifications.push.backends.batch import UserUpdateData
from pcapi.notifications.push.transactional_notifications import TransactionalNotificationData
from pcapi.notifications.push.trigger_events import TrackBatchEventRequest


logger = logging.getLogger(__name__)


class LoggerBackend:
    def update_user_attributes(
        self, batch_api: BatchAPI, user_id: int, attribute_values: dict, can_be_asynchronously_retried: bool = False
    ) -> None:
        logger.info(
            "A request to update user attributes would be sent for user with id=%d with new attributes=%s to api=%s",
            user_id,
            attribute_values,
            batch_api.name,
            extra={"can_be_asynchronously_retried": can_be_asynchronously_retried},
        )

    def update_users_attributes(
        self, users_data: list[UserUpdateData], can_be_asynchronously_retried: bool = False
    ) -> None:
        logger.info(
            "A request to update users attributes would be sent for %d users: %s",
            len(users_data),
            [user.user_id for user in users_data],
            extra={"can_be_asynchronously_retried": can_be_asynchronously_retried},
        )

    def send_transactional_notification(
        self, notification_data: TransactionalNotificationData, can_be_asynchronously_retried: bool = False
    ) -> None:
        logger.info(
            "A request to send a transactional notification would be sent to users with ids=%d, group_id=%s, title=%s, body=%s",
            notification_data.user_ids,
            notification_data.group_id,
            notification_data.message.title,
            notification_data.message.body,
            extra={"can_be_asynchronously_retried": can_be_asynchronously_retried},
        )

    def delete_user_attributes(self, user_id: int, can_be_asynchronously_retried: bool = False) -> None:
        logger.info(
            "A request to delete user attributes would be sent for user with id=%d",
            user_id,
            extra={"can_be_asynchronously_retried": can_be_asynchronously_retried},
        )

    def track_event(
        self, user_id: int, event_name: str, event_payload: dict, can_be_asynchronously_retried: bool = False
    ) -> None:
        logger.info(
            "A request to track event=ue.%s would be sent for user with id=%d",
            event_name,
            user_id,
            extra={"event_payload": event_payload, "can_be_asynchronously_retried": can_be_asynchronously_retried},
        )

    def track_event_bulk(
        self, track_event_data: list[TrackBatchEventRequest], can_be_asynchronously_retried: bool = False
    ) -> None:
        user_ids = [data.user_id for data in track_event_data]
        logger.info(
            "A request to track event bulk would be sent for users ids=%d",
            user_ids,
            extra={"can_be_asynchronously_retried": can_be_asynchronously_retried},
        )
