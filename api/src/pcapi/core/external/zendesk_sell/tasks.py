import logging

from pcapi.celery_tasks.tasks import celery_async_task

from . import serialization


logger = logging.getLogger(__name__)


RATE_LIMIT_PER_TASK_PER_SECOND = 3


@celery_async_task(
    name="tasks.zendesk_sell.default.create_offerer",
    model=serialization.OffererPayload,
    max_per_time_window=RATE_LIMIT_PER_TASK_PER_SECOND,
    time_window_size=1,
)
def create_offerer_task(payload: serialization.OffererPayload) -> None:
    from . import api

    logger.info("create_offerer_task", extra={"offerer_id": payload.offerer_id})
    api.do_create_offerer(payload.offerer_id)


@celery_async_task(
    name="tasks.zendesk_sell.default.update_offerer",
    model=serialization.OffererPayload,
    max_per_time_window=RATE_LIMIT_PER_TASK_PER_SECOND,
    time_window_size=1,
)
def update_offerer_task(payload: serialization.OffererPayload) -> None:
    from . import api

    logger.info("update_offerer_task", extra={"offerer_id": payload.offerer_id})
    api.do_update_offerer(payload.offerer_id)


@celery_async_task(
    name="tasks.zendesk_sell.default.create_venue",
    model=serialization.VenuePayload,
    max_per_time_window=RATE_LIMIT_PER_TASK_PER_SECOND,
    time_window_size=1,
)
def create_venue_task(payload: serialization.VenuePayload) -> None:
    from . import api

    logger.info("create_venue_task", extra={"venue_id": payload.venue_id})
    api.do_create_venue(payload.venue_id)


@celery_async_task(
    name="tasks.zendesk_sell.default.update_venue",
    model=serialization.VenuePayload,
    max_per_time_window=RATE_LIMIT_PER_TASK_PER_SECOND,
    time_window_size=1,
)
def update_venue_task(payload: serialization.VenuePayload) -> None:
    from . import api

    logger.info("update_venue_task", extra={"venue_id": payload.venue_id})
    api.do_update_venue(payload.venue_id)
