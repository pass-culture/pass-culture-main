from typing import Iterable
from typing import Union

from pcapi import settings
from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalEmailData
from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalWithoutTemplateEmailData
from pcapi.utils.module_loading import import_string

from .models import models


def send(
    *,
    recipients: Iterable[str],
    data: Union[dict, SendinblueTransactionalEmailData, SendinblueTransactionalWithoutTemplateEmailData],
) -> bool:
    """Try to send an e-mail and return whether it was successful."""
    if isinstance(recipients, str):
        if settings.IS_RUNNING_TESTS:
            raise ValueError("Recipients should be a sequence, not a single string.")
        recipients = [recipients]
    backend = import_string(settings.EMAIL_BACKEND)
    result = backend().send_mail(recipients=recipients, data=data)
    _save_email(result)
    return result.successful


def _save_email(result: models.MailResult):  # type: ignore [no-untyped-def]
    """Save email to the database with its status"""
    email = models.Email(
        content=result.sent_data,
        status=models.EmailStatus.SENT if result.successful else models.EmailStatus.ERROR,
    )
    # FIXME (dbaty, 2020-02-08): avoid import loop. Again. Yes, it's on my todo list.
    from pcapi.repository import repository

    repository.save(email)
