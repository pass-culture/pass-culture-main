from typing import Iterable

from pcapi import settings
from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalEmailData
from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalWithoutTemplateEmailData
from pcapi.utils.module_loading import import_string

from .models import models  # noqa: F401


def send(
    *,
    recipients: Iterable[str],
    data: dict | SendinblueTransactionalEmailData | SendinblueTransactionalWithoutTemplateEmailData,
) -> bool:
    """Try to send an e-mail and return whether it was successful."""
    if isinstance(recipients, str):
        if settings.IS_RUNNING_TESTS:
            raise ValueError("Recipients should be a sequence, not a single string.")
        recipients = [recipients]
    backend = import_string(settings.EMAIL_BACKEND)
    result = backend().send_mail(recipients=recipients, data=data)
    return result.successful
