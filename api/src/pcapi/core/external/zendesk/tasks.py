import logging

from pcapi.celery_tasks.tasks import celery_async_task
from pcapi.core.external.zendesk import serialization


logger = logging.getLogger(__name__)


@celery_async_task(
    name="tasks.zendesk.default.update_contact_attributes",
    model=serialization.UpdateZendeskAttributesRequest,
    rate_limit="1/s",
)
def update_zendesk_attributes_task(payload: serialization.UpdateZendeskAttributesRequest) -> None:
    from .api import update_contact_attributes

    update_contact_attributes(
        payload.is_new_ticket, payload.ticket_id, payload.zendesk_user_id, payload.email, payload.phone_number
    )
