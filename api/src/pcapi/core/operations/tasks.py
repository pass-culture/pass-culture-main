from pydantic import BaseModel as BaseModelV2

from pcapi.celery_tasks.tasks import celery_async_task
from pcapi.core.operations import models as operations_models
from pcapi.models import db


class RetrieveSpecialEventFromTypeformPayload(BaseModelV2):
    event_id: int


@celery_async_task(
    name="tasks.operations.default.retrieve_special_event_from_typeform",
    model=RetrieveSpecialEventFromTypeformPayload,
)
def retrieve_special_event_from_typeform_task(event_id: int) -> None:
    from pcapi.core.operations.api import retrieve_special_event_from_typeform

    event = (
        db.session.query(operations_models.SpecialEvent)
        .filter(
            operations_models.SpecialEvent.id == event_id,
        )
        .one_or_none()
    )
    if event:
        retrieve_special_event_from_typeform(event)
