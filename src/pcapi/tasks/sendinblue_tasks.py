import logging

from pydantic import BaseModel

from pcapi import settings
from pcapi.core.users.external import sendinblue
from pcapi.models import ApiErrors
from pcapi.tasks.decorator import task


logger = logging.getLogger(__name__)

SENDINBLUE_CONTACTS_QUEUE_NAME = settings.GCP_SENDINBLUE_CONTACTS_QUEUE_NAME


class UpdateSendinblueContactRequest(BaseModel):
    email: str
    attributes: dict
    contact_list_ids: list[int]


@task(SENDINBLUE_CONTACTS_QUEUE_NAME, "/sendinblue/update_contact_attributes")
def update_contact_attributes_task(payload: UpdateSendinblueContactRequest) -> None:
    if not sendinblue.make_update_request(payload):
        raise ApiErrors(status_code=503)
