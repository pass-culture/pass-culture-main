from typing import Iterable

from pcapi import settings
from pcapi.utils.module_loading import import_string

from . import models


def send(
    *,
    recipients: Iterable[str],
    data: models.TransactionalEmailData | models.TransactionalWithoutTemplateEmailData,
) -> bool:
    """Try to send an e-mail and return whether it was successful."""
    if isinstance(recipients, str):
        if settings.IS_RUNNING_TESTS:
            raise ValueError("Recipients should be a sequence, not a single string.")
        recipients = [recipients]
    backend = import_string(settings.EMAIL_BACKEND)
    result = backend().send_mail(recipients=recipients, data=data)
    return result.successful
