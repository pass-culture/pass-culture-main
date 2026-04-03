from brevo_python.rest import ApiException as BrevoApiException

from pcapi import settings
from pcapi.celery_tasks.tasks import celery_async_task

from .serialization import SendTransactionalEmailRequest
from .serialization import UpdateBrevoContactRequest


@celery_async_task(
    name="tasks.mails.priority.update_contact_attributes",
    autoretry_for=(BrevoApiException,),
    model=UpdateBrevoContactRequest,
    max_per_time_window=settings.SENDINBLUE_UPDATE_CONTACT_RATE_LIMIT_THRESHOLD,
    time_window_size=settings.SENDINBLUE_UPDATE_CONTACT_RATE_LIMIT_TIME_WINDOW_SECONDS,
)
def update_contact_attributes_task(payload: UpdateBrevoContactRequest) -> None:
    from pcapi.core.external.brevo import make_update_request

    make_update_request(payload)


@celery_async_task(
    name="tasks.mails.priority.send_transactional_email_primary",
    autoretry_for=(BrevoApiException,),
    model=SendTransactionalEmailRequest,
    max_per_time_window=settings.SENDINBLUE_SEND_EMAIL_PRIMARY_RATE_LIMIT_THRESHOLD,
    time_window_size=settings.SENDINBLUE_SEND_EMAIL_PRIMARY_RATE_LIMIT_TIME_WINDOW_SECONDS,
)
def send_transactional_email_primary_task(payload: SendTransactionalEmailRequest) -> None:
    from pcapi.core.mails.transactional import send_transactional_email

    send_transactional_email(payload)


@celery_async_task(
    name="tasks.mails.default.send_transactional_email_secondary",
    autoretry_for=(BrevoApiException,),
    model=SendTransactionalEmailRequest,
    max_per_time_window=settings.SENDINBLUE_SEND_EMAIL_SECONDARY_RATE_LIMIT_THRESHOLD,
    time_window_size=settings.SENDINBLUE_SEND_EMAIL_SECONDARY_RATE_LIMIT_TIME_WINDOW_SECONDS,
)
def send_transactional_email_secondary_task(payload: SendTransactionalEmailRequest) -> None:
    from pcapi.core.mails.transactional import send_transactional_email

    send_transactional_email(payload)
