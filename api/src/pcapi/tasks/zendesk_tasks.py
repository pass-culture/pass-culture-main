import logging
from typing import Optional

from pcapi.routes.serialization import BaseModel
from pcapi.settings import GCP_ZENDESK_ATTRIBUTES_QUEUE_NAME
from pcapi.tasks.decorator import task


logger = logging.getLogger(__name__)


class UpdateZendeskAttributesRequest(BaseModel):
    is_new_ticket: bool
    ticket_id: int
    zendesk_user_id: int
    email: Optional[str]
    phone_number: Optional[str]


@task(GCP_ZENDESK_ATTRIBUTES_QUEUE_NAME, "/zendesk/update_user_attributes")  # type: ignore [arg-type]
def update_zendesk_attributes_task(payload: UpdateZendeskAttributesRequest) -> None:
    from pcapi.core.users.external.zendesk import update_contact_attributes

    update_contact_attributes(
        payload.is_new_ticket, payload.ticket_id, payload.zendesk_user_id, payload.email, payload.phone_number
    )
