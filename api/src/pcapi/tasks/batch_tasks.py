# TODO: remove this file when batch is called directly by cloudtask and remaining enqueued tasks have been leased

import logging

from pcapi import settings
from pcapi.notifications.push import delete_user_attributes
from pcapi.notifications.push import send_transactional_notification
from pcapi.notifications.push import track_event
from pcapi.notifications.push import track_event_bulk
from pcapi.notifications.push import update_user_attributes
from pcapi.notifications.push.backends.batch import BatchAPI
from pcapi.notifications.push.transactional_notifications import TransactionalNotificationData
from pcapi.notifications.push.trigger_events import TrackBatchEventRequest
from pcapi.notifications.push.trigger_events import TrackBatchEventsRequest
from pcapi.routes.serialization import BaseModel
from pcapi.tasks.decorator import task


logger = logging.getLogger(__name__)


class UpdateBatchAttributesRequest(BaseModel):
    attributes: dict
    user_id: int


class DeleteBatchUserAttributesRequest(BaseModel):
    user_id: int


@task(settings.GCP_BATCH_CUSTOM_DATA_ANDROID_QUEUE_NAME, "/batch/android/update_user_attributes")  # type: ignore[arg-type]
def update_user_attributes_android_task(payload: UpdateBatchAttributesRequest) -> None:
    update_user_attributes(BatchAPI.ANDROID, payload.user_id, payload.attributes, can_be_asynchronously_retried=True)


@task(settings.GCP_BATCH_CUSTOM_DATA_IOS_QUEUE_NAME, "/batch/ios/update_user_attributes")  # type: ignore[arg-type]
def update_user_attributes_ios_task(payload: UpdateBatchAttributesRequest) -> None:
    update_user_attributes(BatchAPI.IOS, payload.user_id, payload.attributes, can_be_asynchronously_retried=True)


@task(settings.GCP_BATCH_CUSTOM_DATA_QUEUE_NAME, "/batch/delete_user_attributes")  # type: ignore[arg-type]
def delete_user_attributes_task(payload: DeleteBatchUserAttributesRequest) -> None:
    delete_user_attributes(payload.user_id, can_be_asynchronously_retried=True)


@task(settings.GCP_BATCH_NOTIFICATION_QUEUE_NAME, "/batch/send_transactional_notification")
def send_transactional_notification_task(payload: TransactionalNotificationData) -> None:
    send_transactional_notification(payload, can_be_asynchronously_retried=True)


@task(settings.GCP_BATCH_CUSTOM_EVENT_QUEUE_NAME, "/batch/track_event")
def track_event_task(payload: TrackBatchEventRequest) -> None:
    track_event(payload.user_id, payload.event_name, payload.event_payload, can_be_asynchronously_retried=True)


@task(settings.GCP_BATCH_CUSTOM_EVENT_QUEUE_NAME, "/batch/track_event_bulk")
def track_event_bulk_task(payload: TrackBatchEventsRequest) -> None:
    track_event_bulk(payload.trigger_events, can_be_asynchronously_retried=True)
