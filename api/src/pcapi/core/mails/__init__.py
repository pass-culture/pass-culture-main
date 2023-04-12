import typing
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
    bcc_recipients: Iterable[str] = None,
) -> bool:
    """Try to send an e-mail and return whether it was successful."""
    if isinstance(recipients, str):
        if settings.IS_RUNNING_TESTS:
            raise ValueError("Recipients should be a sequence, not a single string.")
        recipients = [recipients]
    backend = _get_backend(data)
    result = backend().send_mail(recipients=recipients, bcc_recipients=bcc_recipients, data=data)
    return result.successful


def create_contact(payload: sendinblue_tasks.UpdateSendinblueContactRequest) -> None:
    backend = import_string(settings.EMAIL_BACKEND)
    backend().create_contact(payload)


def _get_backend(data: models.TransactionalEmailData | models.TransactionalWithoutTemplateEmailData) -> type:
    # Do not send unnecessary transactional emails through Sendinblue in EHP
    if (
        (settings.IS_STAGING or settings.IS_TESTING)
        and isinstance(data, models.TransactionalEmailData)
        and not data.template.send_to_ehp
    ):
        return import_string("pcapi.core.mails.backends.logger.LoggerBackend")

    return import_string(settings.EMAIL_BACKEND)
