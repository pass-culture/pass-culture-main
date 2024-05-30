from typing import Iterable

from pcapi import settings
from pcapi.tasks.serialization import sendinblue_tasks
from pcapi.utils.module_loading import import_string

from . import models
from .backends.base import BaseBackend
from .backends.logger import LoggerBackend


def send(
    *,
    recipients: Iterable[str],
    data: models.TransactionalEmailData | models.TransactionalWithoutTemplateEmailData,
    bcc_recipients: Iterable[str] = (),
) -> None:
    """Asynchronously send an email."""
    if isinstance(recipients, str):
        if settings.IS_RUNNING_TESTS:
            raise ValueError("Recipients should be a sequence, not a single string.")
        recipients = [recipients]
    backend = _get_backend(data)
    backend().send_mail(recipients=recipients, bcc_recipients=bcc_recipients, data=data)


def create_contact(payload: sendinblue_tasks.UpdateSendinblueContactRequest) -> None:
    backend = import_string(settings.EMAIL_BACKEND)
    backend().create_contact(payload)


def delete_contact(contact_email: str) -> None:
    backend = import_string(settings.EMAIL_BACKEND)
    backend().delete_contact(contact_email)


def get_contact_url(contact_email: str) -> str | None:
    backend = import_string(settings.EMAIL_BACKEND)
    return backend().get_contact_url(contact_email)


def get_raw_contact_data(contact_email: str) -> dict:
    """Returns all data stored by the email provider on the given contact as a raw dict"""
    backend = import_string(settings.EMAIL_BACKEND)
    return backend().get_raw_contact_data(contact_email)


def _get_backend(data: models.TransactionalEmailData | models.TransactionalWithoutTemplateEmailData) -> type:
    # Do not send unnecessary transactional emails through Sendinblue in EHP
    if (
        (settings.IS_STAGING or settings.IS_TESTING)
        and isinstance(data, models.TransactionalEmailData)
        and not data.template.send_to_ehp
    ):
        return import_string("pcapi.core.mails.backends.logger.LoggerBackend")

    return import_string(settings.EMAIL_BACKEND)
