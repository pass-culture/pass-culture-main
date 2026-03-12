import logging

from pcapi.celery_tasks.tasks import celery_async_task
from pcapi.core.external.batch import api
from pcapi.core.external.batch import serialization


logger = logging.getLogger(__name__)


@celery_async_task("tasks.batch.priority.update_user_attributes", model=serialization.UpdateBatchAttributesRequestV2)
def update_user_attributes_task(
    payload: serialization.UpdateBatchAttributesRequestV2,
) -> None:  # TODO add rate params
    api.update_user_attributes_new(payload.user_id, payload.attributes, can_be_asynchronously_retried=True)


@celery_async_task(
    "tasks.batch.priority.delete_user_attributes", model=serialization.DeleteBatchUserAttributesRequestV2
)
def delete_user_attributes_task(
    payload: serialization.DeleteBatchUserAttributesRequestV2,
) -> None:  # TODO add rate params
    api.delete_user_attributes(payload.user_id, can_be_asynchronously_retried=True)


@celery_async_task(
    name="tasks.batch.priority.send_notification_data",
    model=serialization.TransactionalNotificationDataV2,  # TODO add rate params ?
)
def send_transactional_notification_task(payload: serialization.TransactionalNotificationDataV2) -> None:
    api.send_transactional_notification(payload, can_be_asynchronously_retried=True)


@celery_async_task(
    name="tasks.batch.priority.track_event",
    model=serialization.TrackBatchEventsRequestV2,  # TODO add rate params
)
def track_event_task(payload: serialization.TrackBatchEventRequestV2) -> None:
    api.track_event(payload.user_id, payload.event_name, payload.event_payload, can_be_asynchronously_retried=True)


@celery_async_task(
    name="tasks.batch.priority.track_event_bulk",
    model=serialization.TrackBatchEventsRequestV2,
    # TODO add rate params
)
def track_event_bulk_task(payload: serialization.TrackBatchEventsRequestV2) -> None:
    api.track_event_bulk(payload.trigger_events, can_be_asynchronously_retried=True)
