import logging

from pcapi import settings
from pcapi.core.subscription.ubble import api as ubble_subscription_api
from pcapi.routes.serialization import BaseModel
from pcapi.tasks.decorator import task


logger = logging.getLogger(__name__)

UBBLE_ARCHIVE_ID_PICTURES_QUEUE_NAME = settings.GCP_UBBLE_ARCHIVE_ID_PICTURES_QUEUE_NAME


class StoreIdPictureRequest(BaseModel):
    identification_id: str


@task(UBBLE_ARCHIVE_ID_PICTURES_QUEUE_NAME, "/ubble/store_id_pictures")  # type: ignore [arg-type]
def store_id_pictures_task(payload: StoreIdPictureRequest) -> None:
    try:
        ubble_subscription_api.archive_ubble_user_id_pictures(payload.identification_id)
    except Exception:  # pylint: disable=broad-except
        logger.exception(
            "Could not archive Ubble user id picture",
            extra={"identification_id": payload.identification_id},
        )
