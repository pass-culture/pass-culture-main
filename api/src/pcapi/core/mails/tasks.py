from brevo.core import ApiError as BrevoApiError

from pcapi.celery_tasks.tasks import celery_async_task

from .serialization import SendTransactionalEmailRequest
from .serialization import UpdateBrevoContactRequest


@celery_async_task(
    name="tasks.mails.priority.update_contact_attributes",
    autoretry_for=(BrevoApiError,),
    model=UpdateBrevoContactRequest,
    rate_limit="30/s",
)
def update_contact_attributes_task(payload: UpdateBrevoContactRequest) -> None:
    from pcapi.core.external.brevo import make_update_request

    make_update_request(payload)


@celery_async_task(
    name="tasks.mails.priority.send_transactional_email_primary",
    autoretry_for=(BrevoApiError,),
    model=SendTransactionalEmailRequest,
    rate_limit="8/s",
)
def send_transactional_email_primary_task(payload: SendTransactionalEmailRequest) -> None:
    from pcapi.core.mails.transactional import send_transactional_email

    send_transactional_email(payload)


@celery_async_task(
    name="tasks.mails.default.send_transactional_email_secondary",
    autoretry_for=(BrevoApiError,),
    model=SendTransactionalEmailRequest,
    rate_limit="50/s",
)
def send_transactional_email_secondary_task(payload: SendTransactionalEmailRequest) -> None:
    from pcapi.core.mails.transactional import send_transactional_email

    send_transactional_email(payload)
