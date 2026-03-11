from pydantic import BaseModel as BaseModelV2

from pcapi.routes.serialization import BaseModel

from .models import BatchEvent


class UpdateBatchAttributesRequest(BaseModel):
    attributes: dict
    user_id: int


class DeleteBatchUserAttributesRequest(BaseModel):
    user_id: int


class TrackBatchEventRequest(BaseModel):
    user_id: int
    event_name: BatchEvent
    event_payload: dict


class TrackBatchEventsRequest(BaseModel):
    trigger_events: list[TrackBatchEventRequest]


class TransactionalNotificationMessage(BaseModel):
    body: str
    title: str | None = None


class TransactionalNotificationData(BaseModel):
    group_id: str  # Name of the campaign, useful for analytics purpose
    user_ids: list[int]
    message: TransactionalNotificationMessage
    extra: dict = {}


class TransactionalNotificationMessageV2(BaseModelV2):
    body: str
    title: str | None = None


class TransactionalNotificationDataV2(BaseModelV2):
    group_id: str  # Name of the campaign, useful for analytics purpose
    user_ids: list[int]
    message: TransactionalNotificationMessageV2
    extra: dict = {}
