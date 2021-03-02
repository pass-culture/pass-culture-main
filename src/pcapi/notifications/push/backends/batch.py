from enum import Enum

from pcapi import settings
from pcapi.utils import requests
from pcapi.utils.logger import logger


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
                    f"{settings.BATCH_API_URL}/{api.value}/data/users/{user_id}",
                    headers=self.headers,
                    json={"overwrite": False, "values": attribute_values},
                )
            except Exception as exc:  # pylint: disable=broad-except
                logger.exception(
                    "Error with Batch Custom Data API trying to update attributes of user with id %s: %s", user_id, exc
                )
                return

            if response.status_code != 200:
                logger.error(
                    "Got %d status code from Batch Custom Data API: content=%s", response.status_code, response.content
                )

        make_post_request(BatchAPI.ANDROID)
        make_post_request(BatchAPI.IOS)
