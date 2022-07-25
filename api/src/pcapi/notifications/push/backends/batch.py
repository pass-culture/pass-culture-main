from dataclasses import dataclass
from enum import Enum
import logging

from pcapi import settings
from pcapi.notifications.push.transactional_notifications import TransactionalNotificationData
from pcapi.utils import requests


logger = logging.getLogger(__name__)


API_URL = "https://api.batch.com"


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

    def handle_request(
        self,
        method: str,
        url: str,
        api_name: str,
        payload: dict | list | None = None,
        can_be_asynchronously_retried: bool = False,
    ) -> None:
        try:
            if method == "POST":
                response = requests.post(
                    url, disable_synchronous_retry=can_be_asynchronously_retried, json=payload, headers=self.headers
                )
            elif method == "DELETE":
                response = requests.delete(
                    url, disable_synchronous_retry=can_be_asynchronously_retried, headers=self.headers
                )
            else:
                raise ValueError(f"Invalid method {method}")
        except Exception as exc:
            logger_method = logger.warning if can_be_asynchronously_retried else logger.exception
            logger_method(  # pylint: disable=logging-fstring-interpolation
                f"Exception with Batch {api_name} API", extra={"payload": payload}
            )
            raise requests.ExternalAPIException(is_retryable=True) from exc

        if response.ok:
            return

        if response.status_code >= 500 and can_be_asynchronously_retried:
            logger_method = logger.warning
            is_retryable = True
        else:
            logger_method = logger.error
            is_retryable = False

        logger_method(  # pylint: disable=logging-fstring-interpolation
            f"Error with Batch {api_name} API: {response.status_code}",
            extra={"response_content": response.content, "payload": payload},
        )
        raise requests.ExternalAPIException(is_retryable=is_retryable)

    def update_user_attributes(
        self, batch_api: BatchAPI, user_id: int, attribute_values: dict, can_be_asynchronously_retried: bool = False
    ) -> None:
        self.handle_request(
            "POST",
            f"{API_URL}/1.0/{batch_api.value}/data/users/{user_id}",
            api_name="update_user_attributes",
            can_be_asynchronously_retried=can_be_asynchronously_retried,
            payload={"overwrite": False, "values": attribute_values},
        )

    def update_users_attributes(
        self, users_data: list[UserUpdateData], can_be_asynchronously_retried: bool = False
    ) -> None:
        def payload_template(user: UserUpdateData) -> dict:
            return {
                "id": user.user_id,
                "update": {"overwrite": False, "values": user.attributes},
            }

        def make_post_request(api: BatchAPI) -> None:
            self.handle_request(
                "POST",
                f"{API_URL}/1.0/{api.value}/data/users/",
                api_name="update_userS_attributes",
                can_be_asynchronously_retried=can_be_asynchronously_retried,
                payload=[payload_template(user) for user in users_data],
            )

        make_post_request(BatchAPI.ANDROID)
        make_post_request(BatchAPI.IOS)

    def send_transactional_notification(
        self, notification_data: TransactionalNotificationData, can_be_asynchronously_retried: bool = False
    ) -> None:
        def make_post_request(api: BatchAPI) -> None:
            self.handle_request(
                "POST",
                f"{API_URL}/1.1/{api.value}/transactional/send",
                api_name="transactional_notification",
                can_be_asynchronously_retried=can_be_asynchronously_retried,
                payload={
                    "group_id": notification_data.group_id,
                    "recipients": {"custom_ids": [str(user_id) for user_id in notification_data.user_ids]},
                    "message": {
                        "title": notification_data.message.title,
                        "body": notification_data.message.body,
                    },
                    **notification_data.extra,  # type: ignore [arg-type]
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
            url = f"{API_URL}/1.0/{api.value}/data/users/{user_id}"
            self.handle_request(
                "DELETE",
                url,
                api_name="delete_user_attributes",
                can_be_asynchronously_retried=can_be_asynchronously_retried,
            )
