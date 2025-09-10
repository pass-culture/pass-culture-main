from brevo_python.rest import ApiException as SendinblueApiException

from pcapi.celery_tasks.tasks import celery_async_task
from pcapi.tasks.serialization.sendinblue_tasks import SendTransactionalEmailRequest
from pcapi.tasks.serialization.sendinblue_tasks import UpdateSendinblueContactRequest


@celery_async_task(
    name="tasks.mails.priority.update_contact_attributes",
    autoretry_for=(SendinblueApiException,),
    model=UpdateSendinblueContactRequest,
)
def update_contact_attributes_task_celery(payload: UpdateSendinblueContactRequest) -> None:
    from pcapi.core.external import sendinblue

    sendinblue.make_update_request(payload)


@celery_async_task(
    name="tasks.mails.priority.send_transactional_email_primary",
    autoretry_for=(SendinblueApiException,),
    model=SendTransactionalEmailRequest,
)
def send_transactional_email_primary_task_celery(payload: SendTransactionalEmailRequest) -> None:
    from pcapi.core.mails.transactional import send_transactional_email

    send_transactional_email(payload)


@celery_async_task(
    name="tasks.mails.default.send_transactional_email_secondary",
    autoretry_for=(SendinblueApiException,),
    model=SendTransactionalEmailRequest,
)
def send_transactional_email_secondary_task_celery(payload: SendTransactionalEmailRequest) -> None:
    from pcapi.core.mails.transactional import send_transactional_email

    send_transactional_email(payload)
