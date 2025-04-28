from pcapi.core.operations import models as operations_models
from pcapi.models import db
from pcapi.workers import worker
from pcapi.workers.decorators import job


@job(worker.low_queue)
def retrieve_special_event_from_typeform_job(event_id: int) -> None:
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
