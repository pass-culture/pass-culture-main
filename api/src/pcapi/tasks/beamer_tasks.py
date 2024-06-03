import logging

from pcapi import settings
from pcapi.tasks.decorator import task
from pcapi.tasks.serialization.external_pro_tasks import UpdateProAttributesRequest


logger = logging.getLogger(__name__)

BEAMER_PRO_QUEUE_NAME = settings.GCP_BEAMER_PRO_QUEUE_NAME


# Deduplicate and delay by 12 hours.
# See api/src/pcapi/tasks/sendinblue_tasks.py comment for more details
@task(BEAMER_PRO_QUEUE_NAME, "/beamer/update_pro_attributes", True, 43_200)  # type: ignore[arg-type]
def update_beamer_pro_attributes_task(payload: UpdateProAttributesRequest) -> None:
    from pcapi.connectors import beamer
    from pcapi.core.external.attributes.api import get_pro_attributes

    logger.info("update_beamer_pro_attributes_task", extra={"email": payload.email, "time_id": payload.time_id})

    attributes = get_pro_attributes(payload.email)
    beamer.update_beamer_user(attributes)
