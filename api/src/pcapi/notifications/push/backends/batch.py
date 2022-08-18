from dataclasses import dataclass
from enum import Enum
import logging

from pcapi import settings
from pcapi.notifications.push import models as push_models
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

    def update_user_attributes(
        self, batch_api: BatchAPI, user_id: int, attribute_values: dict, can_be_asynchronously_retried: bool = False
    ) -> push_models.UpdateAttributeRequestResult:
        try:
            response = requests.post(
                f"{settings.BATCH_API_URL}/1.0/{batch_api.value}/data/users/{user_id}",
                disable_synchronous_retry=can_be_asynchronously_retried,
                headers=self.headers,
                json={"overwrite": False, "values": attribute_values},
            )
        except Exception:  # pylint: disable=broad-except
            logger.exception(
                "Error with Batch Custom Data API trying to update attributes",
                extra={"user_id": user_id, "attribute_values": attribute_values, "api": batch_api.name},
            )
            return push_models.UpdateAttributeRequestResult(should_retry=True)

        if not response.ok:
            logger.error(  # pylint: disable=logging-fstring-interpolation
                f"Got {response.status_code} status code from Batch Custom Data API",
                extra={"response_content": response.content},
            )

        return push_models.UpdateAttributeRequestResult(should_retry=False)

    def update_users_attributes(
        self, users_data: list[UserUpdateData], can_be_asynchronously_retried: bool = False
    ) -> None:
        def payload_template(user: UserUpdateData) -> dict:
            return {
                "id": user.user_id,
                "update": {"overwrite": False, "values": user.attributes},
            }

        def make_post_request(api: BatchAPI) -> None:
            try:
                response = requests.post(
                    f"{settings.BATCH_API_URL}/1.0/{api.value}/data/users/",
                    disable_synchronous_retry=can_be_asynchronously_retried,
                    headers=self.headers,
                    json=[payload_template(user) for user in users_data],
                )
            except Exception:  # pylint: disable=broad-except
                logger.exception(
                    "Error with Batch Custom Data API trying to update attributes of users",
                    extra={"users": {user.user_id for user in users_data}, "api": api.name},
                )
                return

            if not response.ok:
                logger.error(  # pylint: disable=logging-fstring-interpolation
                    f"Got {response.status_code} status code from Batch Custom Data API (batch update)",
                    response.status_code,
                    extra={
                        "users": {user.user_id for user in users_data},
                        "api": api.name,
                        "response_content": response.content,
                        "status_code": response.status_code,
                    },
                )

        make_post_request(BatchAPI.ANDROID)
        make_post_request(BatchAPI.IOS)

    def send_transactional_notification(
        self, notification_data: TransactionalNotificationData, can_be_asynchronously_retried: bool = False
    ) -> None:
        def make_post_request(api: BatchAPI) -> None:
            try:
                response = requests.post(
                    f"{settings.BATCH_API_URL}/1.1/{api.value}/transactional/send",
                    disable_synchronous_retry=can_be_asynchronously_retried,
                    headers=self.headers,
                    json={
                        "group_id": notification_data.group_id,
                        "recipients": {"custom_ids": [str(user_id) for user_id in notification_data.user_ids]},
                        "message": {
                            "title": notification_data.message.title,
                            "body": notification_data.message.body,
                        },
                        **notification_data.extra,  # type: ignore [arg-type]
                    },
                )
            except Exception as exc:  # pylint: disable=broad-except
                logger.exception(
                    "Error with Batch Transactional API trying to send group_id=%s notification to users with ids=%s: %s",
                    notification_data.group_id,
                    notification_data.user_ids,
                    exc,
                    extra={
                        "api": api.name,
                        "group_id": notification_data.group_id,
                        "user_ids": notification_data.user_ids,
                    },
                )
                return

            if not response.ok:
                logger.error(
                    "Got %d status code from Batch Transactional API: content=%s",
                    response.status_code,
                    response.content,
                    extra={
                        "api": api.name,
                        "status_code": response.status_code,
                        "group_id": notification_data.group_id,
                        "user_ids": notification_data.user_ids,
                    },
                )

        make_post_request(BatchAPI.ANDROID)
        make_post_request(BatchAPI.IOS)

    def delete_user_attributes(self, user_id: int, can_be_asynchronously_retried: bool = False) -> None:
        """
        To be used as an internal cloud task since cloud tasks do not
        accept DELETE http methods.
        """
        for api in (BatchAPI.IOS, BatchAPI.ANDROID):
            url = f"{settings.BATCH_API_URL}/1.0/{api.value}/data/users/{user_id}"
            try:
                response = requests.delete(
                    url,
                    headers=self.headers,
                    disable_synchronous_retry=can_be_asynchronously_retried,
                )
            except Exception as exc:  # pylint: disable=broad-except
                logger.exception(
                    "Could not delete batch user: %s",
                    exc,
                    extra={"user_id": user_id, "api": str(api)},
                )
            else:
                if response.status_code != 200:
                    logger.error(
                        "Got %d status code from Batch Custom Data API: content=%s",
                        response.status_code,
                        response.content,
                    )
