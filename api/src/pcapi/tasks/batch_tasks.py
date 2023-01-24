# TODO: remove this file when batch is called directly by cloudtask and remaining enqueued tasks have been leased

import logging

from pcapi import settings
import pcapi.notifications.push as push_notifications
from pcapi.notifications.push.backends.batch import BatchAPI
from pcapi.notifications.push.transactional_notifications import TransactionalNotificationData
from pcapi.routes.serialization import BaseModel
from pcapi.tasks.decorator import task


logger = logging.getLogger(__name__)


class UpdateBatchAttributesRequest(BaseModel):
    attributes: dict
    user_id: int


class DeleteBatchUserAttributesRequest(BaseModel):
    user_id: int


class TrackBatchEventRequest(BaseModel):
    user_id: int
    event_name: push_notifications.BatchEvent
    event_payload: dict


class BulkTrackBatchEventRequest(BaseModel):
    user_ids: list[int]
    event_name: push_notifications.BatchEvent
    event_payload: dict


@task(settings.GCP_BATCH_CUSTOM_DATA_ANDROID_QUEUE_NAME, "/batch/android/update_user_attributes")  # type: ignore [arg-type]
def update_user_attributes_android_task(payload: UpdateBatchAttributesRequest) -> None:
    push_notifications.update_user_attributes(
        BatchAPI.ANDROID, payload.user_id, payload.attributes, can_be_asynchronously_retried=True
    )


@task(settings.GCP_BATCH_CUSTOM_DATA_IOS_QUEUE_NAME, "/batch/ios/update_user_attributes")  # type: ignore [arg-type]
def update_user_attributes_ios_task(payload: UpdateBatchAttributesRequest) -> None:
    push_notifications.update_user_attributes(
        BatchAPI.IOS, payload.user_id, payload.attributes, can_be_asynchronously_retried=True
    )


@task(settings.GCP_BATCH_CUSTOM_DATA_QUEUE_NAME, "/batch/delete_user_attributes")  # type: ignore [arg-type]
def delete_user_attributes_task(payload: DeleteBatchUserAttributesRequest) -> None:
    push_notifications.delete_user_attributes(payload.user_id, can_be_asynchronously_retried=True)


@task(settings.GCP_BATCH_NOTIFICATION_QUEUE_NAME, "/batch/send_transactional_notification")
def send_transactional_notification_task(payload: TransactionalNotificationData) -> None:
    push_notifications.send_transactional_notification(payload, can_be_asynchronously_retried=True)


@task(settings.GCP_BATCH_CUSTOM_EVENT_QUEUE_NAME, "/batch/track_event")
def track_event_task(payload: TrackBatchEventRequest) -> None:
    push_notifications.track_event(
        payload.user_id, payload.event_name, payload.event_payload, can_be_asynchronously_retried=True
    )


@task(settings.GCP_BATCH_CUSTOM_EVENT_QUEUE_NAME, "/batch/track_event/bulk")
def track_event_for_multiple_users_task(payload: BulkTrackBatchEventRequest) -> None:
    push_notifications.track_event_for_multiple_users(
        payload.user_ids, payload.event_name, payload.event_payload, can_be_asynchronously_retried=True
    )
