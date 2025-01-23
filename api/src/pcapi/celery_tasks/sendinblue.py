from brevo_python.rest import ApiException as SendinblueApiException
from celery import shared_task

from pcapi.core.external import sendinblue
from pcapi.core.mails.transactional.send_transactional_email import send_transactional_email
from pcapi.tasks.serialization.sendinblue_tasks import SendTransactionalEmailRequest
from pcapi.tasks.serialization.sendinblue_tasks import UpdateSendinblueContactRequest


@shared_task(name="mails.tasks.update_contact_attributes", autoretry_for=(SendinblueApiException,), retry_backoff=True)
def update_contact_attributes_task_celery(payload: UpdateSendinblueContactRequest) -> None:
    sendinblue.make_update_request(payload)


@shared_task(
    name="mails.tasks.send_transactional_email_primary", autoretry_for=(SendinblueApiException,), retry_backoff=True
)
def send_transactional_email_primary_task_celery(payload: SendTransactionalEmailRequest) -> None:
    send_transactional_email(payload)


@shared_task(
    name="mails.tasks.send_transactional_email_secondary", autoretry_for=(SendinblueApiException,), retry_backoff=True
)
def send_transactional_email_secondary_task_celery(payload: SendTransactionalEmailRequest) -> None:
    send_transactional_email(payload)
