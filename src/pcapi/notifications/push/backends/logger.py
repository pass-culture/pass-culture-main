from pcapi.notifications.push.transactional_notifications import TransactionalNotificationData
from pcapi.utils.logger import logger


class LoggerBackend:
    def update_user_attributes(self, user_id: int, attribute_values: dict) -> None:
        logger.info(
            "A request to update user attributes would be sent for user with id=%d with new attributes=%s",
            user_id,
            attribute_values,
        )

    def send_transactional_notification(self, notification_data: TransactionalNotificationData) -> None:
        logger.info(
            "A request to send a transactional notification would be sent to users with ids=%d, group_id=%s, title=%s, body=%s",
            notification_data.user_ids,
            notification_data.group_id,
            notification_data.message.title,
            notification_data.message.body,
        )
