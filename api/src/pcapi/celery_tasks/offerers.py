import datetime
import logging
import time

from brevo_python.rest import ApiException as SendinblueApiException
from flask import current_app

from pcapi.celery_tasks.tasks import celery_async_task
from pcapi.core.offerers import tasks as offerer_tasks


logger = logging.getLogger(__name__)

CHECK_OFFERER_SIREN_LOCK_NAME = "check_offerer_siren:lock"
CHECK_OFFERER_SIREN_RATE_LIMIT_PER_MINUTE = 10


@celery_async_task(
    name="tasks.offerers.default.check_active_offerer",
    autoretry_for=(SendinblueApiException,),
    model=offerer_tasks.CheckOffererSirenRequest,
)
def check_offerer_siren_task_celery(payload: offerer_tasks.CheckOffererSirenRequest) -> None:
    logger.info("****************check_offerer_siren_task_celery (1) %s", datetime.datetime.now().isoformat())
    while (ttl := current_app.redis_client.ttl(CHECK_OFFERER_SIREN_LOCK_NAME)) > 0:
        time.sleep(ttl)
    current_app.redis_client.set(
        CHECK_OFFERER_SIREN_LOCK_NAME, "1", ex=60.0 / CHECK_OFFERER_SIREN_RATE_LIMIT_PER_MINUTE
    )

    logger.info("****************check_offerer_siren_task_celery (2) %s", datetime.datetime.now().isoformat())
    offerer_tasks.check_offerer_siren(payload)
