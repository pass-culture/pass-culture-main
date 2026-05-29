import logging

from pcapi.celery_tasks.tasks import celery_async_task
from pcapi.core.external.batch import api
from pcapi.core.external.batch import serialization


logger = logging.getLogger(__name__)


@celery_async_task(
    "tasks.batch.priority.update_user_attributes",
    model=serialization.UpdateBatchAttributesRequest,
    max_per_time_window=3000,
)
def update_user_attributes_task(
    payload: serialization.UpdateBatchAttributesRequest,
) -> None:
    api.update_user_attributes(payload.user_id, payload.attributes, can_be_asynchronously_retried=True)


@celery_async_task(
    "tasks.batch.priority.delete_user_attributes",
    model=serialization.DeleteBatchUserAttributesRequest,
    max_per_time_window=180,
)
def delete_user_attributes_task(
    payload: serialization.DeleteBatchUserAttributesRequest,
) -> None:
    api.delete_user_attributes(payload.user_id, can_be_asynchronously_retried=True)


@celery_async_task(
    name="tasks.batch.priority.send_notification_data",
    model=serialization.TransactionalNotificationData,
    max_per_time_window=480,
)
def send_transactional_notification_task(payload: serialization.TransactionalNotificationData) -> None:
    api.send_transactional_notification(payload, can_be_asynchronously_retried=True)


@celery_async_task(
    name="tasks.batch.priority.track_event",
    model=serialization.TrackBatchEventRequest,
    max_per_time_window=3000,
)
def track_event_task(payload: serialization.TrackBatchEventRequest) -> None:
    api.track_event(payload.user_id, payload.event_name, payload.event_payload, can_be_asynchronously_retried=True)


@celery_async_task(
    name="tasks.batch.priority.track_event_bulk",
    model=serialization.TrackBatchEventsRequest,
    max_per_time_window=3000,
)
def track_event_bulk_task(payload: serialization.TrackBatchEventsRequest) -> None:
    api.track_event_bulk(payload.trigger_events, can_be_asynchronously_retried=True)
