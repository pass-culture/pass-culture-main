from typing import Iterable
from typing import Union

from pcapi import settings
from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalEmailData
from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalWithoutTemplateEmailData
from pcapi.utils.module_loading import import_string

from .models import models


def get_email_backend(send_with_sendinblue: bool) -> str:
    if send_with_sendinblue:
        return settings.EMAIL_BACKEND
    return settings.MAILJET_EMAIL_BACKEND


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
    send_with_sendinblue = isinstance(
        data, (SendinblueTransactionalEmailData, SendinblueTransactionalWithoutTemplateEmailData)
    )
    backend = import_string(get_email_backend(send_with_sendinblue))
    result = backend().send_mail(recipients=recipients, data=data)
    return result.successful
