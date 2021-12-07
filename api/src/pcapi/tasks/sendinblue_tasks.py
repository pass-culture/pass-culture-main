import logging

from pcapi import settings
from pcapi.core.mails.transactional.send_transactional_email import send_transactional_email
from pcapi.core.users.external import sendinblue
from pcapi.models.api_errors import ApiErrors
from pcapi.tasks.decorator import task
from pcapi.tasks.serialization.sendinblue_tasks import SendTransactionalEmailRequest
from pcapi.tasks.serialization.sendinblue_tasks import UpdateSendinblueContactRequest


logger = logging.getLogger(__name__)

SENDINBLUE_CONTACTS_QUEUE_NAME = settings.GCP_SENDINBLUE_CONTACTS_QUEUE_NAME
SENDINBLUE_TRANSACTIONAL_EMAILS_PRIMARY_QUEUE_NAME = settings.GCP_SENDINBLUE_TRANSACTIONAL_EMAILS_PRIMARY_QUEUE_NAME
SENDINBLUE_TRANSACTIONAL_EMAILS_SECONDARY_QUEUE_NAME = settings.GCP_SENDINBLUE_TRANSACTIONAL_EMAILS_SECONDARY_QUEUE_NAME


@task(SENDINBLUE_CONTACTS_QUEUE_NAME, "/sendinblue/update_contact_attributes")
def update_contact_attributes_task(payload: UpdateSendinblueContactRequest) -> None:
    if not sendinblue.make_update_request(payload):
        raise ApiErrors()


@task(SENDINBLUE_TRANSACTIONAL_EMAILS_PRIMARY_QUEUE_NAME, "/sendinblue/send-transactional-email-primary")
def send_transactional_email_primary_task(payload: SendTransactionalEmailRequest) -> None:
    if not send_transactional_email(payload):
        raise ApiErrors()


@task(SENDINBLUE_TRANSACTIONAL_EMAILS_SECONDARY_QUEUE_NAME, "/sendinblue/send-transactional-email-secondary")
def send_transactional_email_secondary_task(payload: SendTransactionalEmailRequest) -> None:
    if not send_transactional_email(payload):
        raise ApiErrors()
