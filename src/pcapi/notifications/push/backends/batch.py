from dataclasses import dataclass
from enum import Enum
import logging

from pcapi import settings
from pcapi.notifications.push.transactional_notifications import TransactionalNotificationData
from pcapi.utils import requests


logger = logging.getLogger(__name__)


@dataclass
class UserUpdateData:
    user_id: str
    attributes: dict


class BatchAPI(Enum):
    IOS = settings.BATCH_IOS_API_KEY
    ANDROID = settings.BATCH_ANDROID_API_KEY


class BatchBackend:
    def __init__(self) -> None:
        super().__init__()
        self.headers = {"Content-Type": "application/json", "X-Authorization": settings.BATCH_SECRET_API_KEY}

    def update_user_attributes(self, user_id: int, attribute_values: dict) -> None:
        def make_post_request(api: BatchAPI) -> None:
            try:
                response = requests.post(
                    f"{settings.BATCH_API_URL}/1.0/{api.value}/data/users/{user_id}",
                    headers=self.headers,
                    json={"overwrite": False, "values": attribute_values},
                )
            except Exception as exc:  # pylint: disable=broad-except
                logger.exception(
                    "Error with Batch Custom Data API trying to update attributes of user with id %s: %s", user_id, exc
                )
                return

            if not response.ok:
                logger.error(
                    "Got %d status code from Batch Custom Data API: content=%s", response.status_code, response.content
                )

        make_post_request(BatchAPI.ANDROID)
        make_post_request(BatchAPI.IOS)

    def update_users_attributes(self, users_data: list[UserUpdateData]) -> None:
        def payload_template(user: UserUpdateData) -> dict:
            return {
                "id": user.user_id,
                "update": {"overwrite": False, "values": user.attributes},
            }

        def make_post_request(api: BatchAPI) -> None:
            try:
                response = requests.post(
                    f"{settings.BATCH_API_URL}/1.0/{api.value}/data/users/",
                    headers=self.headers,
                    json=[payload_template(user) for user in users_data],
                )
            except Exception as exc:  # pylint: disable=broad-except
                logger.exception("Error with Batch Custom Data API trying to update attributes of users: %s", exc)
                return

            if not response.ok:
                logger.error(
                    "Got %d status code from Batch Custom Data API (batch update): content=%s",
                    response.status_code,
                    response.content,
                )

        make_post_request(BatchAPI.ANDROID)
        make_post_request(BatchAPI.IOS)

    def send_transactional_notification(self, notification_data: TransactionalNotificationData) -> None:
        def make_post_request(api: BatchAPI) -> None:
            try:
                response = requests.post(
                    f"{settings.BATCH_API_URL}/1.1/{api.value}/transactional/send",
                    headers=self.headers,
                    json={
                        "group_id": notification_data.group_id,
                        "recipients": {"custom_ids": [str(user_id) for user_id in notification_data.user_ids]},
                        "message": {
                            "title": notification_data.message.title,
                            "body": notification_data.message.body,
                        },
                        **notification_data.extra,
                    },
                )
            except Exception as exc:  # pylint: disable=broad-except
                logger.exception(
                    "Error with Batch Transactional API trying to send group_id=%s notification to users with ids=%s: %s",
                    notification_data.group_id,
                    notification_data.user_ids,
                    exc,
                )
                return

            if not response.ok:
                logger.error(
                    "Got %d status code from Batch Transactional API: content=%s",
                    response.status_code,
                    response.content,
                )

        make_post_request(BatchAPI.ANDROID)
        make_post_request(BatchAPI.IOS)
