import logging

from pydantic import BaseModel as BaseModelV2

from pcapi import settings
from pcapi.celery_tasks.tasks import celery_async_task
from pcapi.celery_tasks.tasks import deduplicate
from pcapi.core.external.attributes.api import get_pro_attributes
from pcapi.core.external.beamer.api import update_beamer_user
from pcapi.tasks.decorator import task
from pcapi.tasks.serialization.external_pro_tasks import UpdateProAttributesRequest


logger = logging.getLogger(__name__)

BEAMER_PRO_QUEUE_NAME = settings.GCP_BEAMER_PRO_QUEUE_NAME


# Deduplicate and delay by 12 hours.
# See api/src/pcapi/tasks/brevo_tasks.py comment for more details
@task(BEAMER_PRO_QUEUE_NAME, "/beamer/update_pro_attributes", True, 43_200)
def update_beamer_pro_attributes_task(payload: UpdateProAttributesRequest) -> None:
    logger.info("update_beamer_pro_attributes_task", extra={"email": payload.email, "time_id": payload.time_id})

    attributes = get_pro_attributes(payload.email)
    update_beamer_user(attributes)


class UpdateBeamerProAttributesPayload(BaseModelV2):
    email: str
    time_id: str


# Deduplicate and delay by 12 hours.
# See api/src/pcapi/tasks/sendinblue_tasks.py comment for more details
@celery_async_task(
    name="tasks.beamer.default.update_beamer_pro_attributes",
    model=UpdateBeamerProAttributesPayload,
    max_per_time_window=12345,  # TODO
    time_window_size=12345,  # TODO
)
@deduplicate(ttl=43_200)
def update_beamer_pro_attributes_task_celery(payload: UpdateBeamerProAttributesPayload) -> None:
    logger.info("update_beamer_pro_attributes_task", extra={"email": payload.email, "time_id": payload.time_id})

    attributes = get_pro_attributes(payload.email)
    update_beamer_user(attributes)
