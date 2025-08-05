from functools import partial
from typing import Iterable

from pcapi import settings
from pcapi.models.feature import FeatureToggle
from pcapi.tasks.serialization import sendinblue_tasks
from pcapi.utils.module_loading import import_string
from pcapi.utils.transaction_manager import on_commit

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
    use_pro_subaccount = data.template.use_pro_subaccount if isinstance(data, models.TransactionalEmailData) else False
    on_commit(
        partial(
            backend(use_pro_subaccount).send_mail,
            recipients=recipients,
            bcc_recipients=bcc_recipients,
            data=data,
        )
    )


def create_contact(payload: sendinblue_tasks.UpdateSendinblueContactRequest) -> None:
    backend = import_string(settings.EMAIL_BACKEND)
    backend(payload.use_pro_subaccount).create_contact(payload)


def delete_contact(contact_email: str, use_pro_subaccount: bool) -> None:
    backend = import_string(settings.EMAIL_BACKEND)
    backend(use_pro_subaccount).delete_contact(contact_email)


def get_contact_url(contact_email: str, use_pro_subaccount: bool) -> str | None:
    backend = import_string(settings.EMAIL_BACKEND)
    return backend(use_pro_subaccount).get_contact_url(contact_email)


def get_raw_contact_data(contact_email: str, use_pro_subaccount: bool) -> dict:
    """Returns all data stored by the email provider on the given contact as a raw dict"""
    backend = import_string(settings.EMAIL_BACKEND)
    return backend(use_pro_subaccount).get_raw_contact_data(contact_email)


def _get_backend(data: models.TransactionalEmailData | models.TransactionalWithoutTemplateEmailData) -> type:
    # Do not send unnecessary transactional emails through Sendinblue in EHP
    if (
        (settings.IS_STAGING or settings.IS_TESTING)
        and isinstance(data, models.TransactionalEmailData)
        and not data.template.send_to_ehp
    ):
        if FeatureToggle.SEND_ALL_EMAILS_TO_EHP.is_active():
            return import_string(settings.EMAIL_BACKEND)
        return import_string("pcapi.core.mails.backends.logger.LoggerBackend")
    return import_string(settings.EMAIL_BACKEND)
