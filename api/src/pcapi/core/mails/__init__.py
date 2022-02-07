from typing import Iterable
from typing import Union

from pcapi import settings
from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalEmailData
from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalWithoutTemplateEmailData
from pcapi.models.feature import FeatureToggle
from pcapi.utils.module_loading import import_string

from .models import models


# TODO: CorentinN - remove this when all transactional emails use Sendinblue
def get_email_backend(send_with_sendinblue: bool) -> str:
    if send_with_sendinblue and FeatureToggle.ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS.is_active():
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
    _save_email(result)
    return result.successful


def _save_email(result: models.MailResult):
    """Save email to the database with its status"""
    email = models.Email(
        content=result.sent_data,
        status=models.EmailStatus.SENT if result.successful else models.EmailStatus.ERROR,
    )
    # FIXME (dbaty, 2020-02-08): avoid import loop. Again. Yes, it's on my todo list.
    from pcapi.repository import repository

    repository.save(email)
