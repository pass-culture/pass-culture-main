# TODO: remove this file when batch is called directly by cloudtask and remaining enqueued tasks have been leased

import logging

from pydantic import BaseModel

from pcapi import settings
from pcapi.notifications.push import update_user_attributes_with_legacy_internal_task
from pcapi.tasks.decorator import task


logger = logging.getLogger(__name__)

BATCH_CUSTOM_DATA_QUEUE_NAME = settings.GCP_BATCH_CUSTOM_DATA_QUEUE_NAME


class UpdateBatchAttributesRequest(BaseModel):
    user_id: int
    attributes: dict


@task(BATCH_CUSTOM_DATA_QUEUE_NAME, "/batch/update_user_attributes")
def update_user_attributes_task(payload: UpdateBatchAttributesRequest) -> None:
    update_user_attributes_with_legacy_internal_task(payload.user_id, payload.attributes)
