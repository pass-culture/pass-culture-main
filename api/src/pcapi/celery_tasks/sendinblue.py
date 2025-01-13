from celery import shared_task

from pcapi.core.external import sendinblue
from pcapi.core.mails.transactional.send_transactional_email import send_transactional_email
from pcapi.tasks.serialization.sendinblue_tasks import SendTransactionalEmailRequest
from pcapi.tasks.serialization.sendinblue_tasks import UpdateSendinblueContactRequest


@shared_task(name="mails.tasks.update_contact_attributes", acks_late=True)
def update_contact_attributes_task_celery(payload: UpdateSendinblueContactRequest) -> None:
    sendinblue.make_update_request(payload)


@shared_task(name="mails.tasks.send_transactional_email_primary", acks_late=True)
def send_transactional_email_primary_task_celery(payload: SendTransactionalEmailRequest) -> None:
    send_transactional_email(payload)


@shared_task(name="mails.tasks.send_transactional_email_secondary", acks_late=True)
def send_transactional_email_secondary_task_celery(payload: SendTransactionalEmailRequest) -> None:
    send_transactional_email(payload)
