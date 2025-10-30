from brevo_python.rest import ApiException as SendinblueApiException

from pcapi import settings
from pcapi.celery_tasks.tasks import celery_async_task
from pcapi.tasks.serialization.sendinblue_tasks import SendTransactionalEmailRequest
from pcapi.tasks.serialization.sendinblue_tasks import UpdateSendinblueContactRequest


@celery_async_task(
    name="tasks.mails.priority.update_contact_attributes",
    autoretry_for=(SendinblueApiException,),
    model=UpdateSendinblueContactRequest,
    max_per_time_window=settings.SENDINBLUE_UPDATE_CONTACT_RATE_LIMIT_THRESHOLD,
    time_window_size=settings.SENDINBLUE_UPDATE_CONTACT_RATE_LIMIT_TIME_WINDOW_SECONDS,
)
def update_contact_attributes_task_celery(payload: UpdateSendinblueContactRequest) -> None:
    from pcapi.core.external import sendinblue

    sendinblue.make_update_request(payload)


@celery_async_task(
    name="tasks.mails.priority.send_transactional_email_primary",
    autoretry_for=(SendinblueApiException,),
    model=SendTransactionalEmailRequest,
    max_per_time_window=settings.SENDINBLUE_SEND_EMAIL_PRIMARY_RATE_LIMIT_THRESHOLD,
    time_window_size=settings.SENDINBLUE_SEND_EMAIL_PRIMARY_RATE_LIMIT_TIME_WINDOW_SECONDS,
)
def send_transactional_email_primary_task_celery(payload: SendTransactionalEmailRequest) -> None:
    from pcapi.core.mails.transactional import send_transactional_email

    send_transactional_email(payload)


@celery_async_task(
    name="tasks.mails.default.send_transactional_email_secondary",
    autoretry_for=(SendinblueApiException,),
    model=SendTransactionalEmailRequest,
    max_per_time_window=settings.SENDINBLUE_SEND_EMAIL_SECONDARY_RATE_LIMIT_THRESHOLD,
    time_window_size=settings.SENDINBLUE_SEND_EMAIL_SECONDARY_RATE_LIMIT_TIME_WINDOW_SECONDS,
)
def send_transactional_email_secondary_task_celery(payload: SendTransactionalEmailRequest) -> None:
    from pcapi.core.mails.transactional import send_transactional_email

    send_transactional_email(payload)
