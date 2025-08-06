import typing
from functools import partial

from pcapi import settings
from pcapi.models.feature import FeatureToggle
from pcapi.tasks.serialization import sendinblue_tasks
from pcapi.utils.module_loading import import_string
from pcapi.utils.transaction_manager import on_commit

from . import models


if typing.TYPE_CHECKING:
    from pcapi.core.mails.backends.logger import LoggerBackend
    from pcapi.core.mails.backends.sendinblue import SendinblueBackend
    from pcapi.core.mails.backends.sendinblue import ToDevSendinblueBackend
    from pcapi.core.mails.backends.testing import TestingBackend

    EmailBackend = type[LoggerBackend | SendinblueBackend | ToDevSendinblueBackend | TestingBackend]


def send(
    *,
    recipients: typing.Iterable[str],
    data: models.TransactionalEmailData | models.TransactionalWithoutTemplateEmailData,
    bcc_recipients: typing.Iterable[str] = (),
) -> None:
    """Asynchronously send an email."""
    if isinstance(recipients, str):
        if settings.IS_RUNNING_TESTS:
            raise ValueError("Recipients should be a sequence, not a single string.")
        recipients = [recipients]
    backend = _get_backend_from_email_data(data)
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
    backend = _get_backend()
    backend(payload.use_pro_subaccount).create_contact(payload)


def delete_contact(contact_email: str, use_pro_subaccount: bool) -> None:
    backend = _get_backend()
    backend(use_pro_subaccount).delete_contact(contact_email)


def get_contact_url(contact_email: str, use_pro_subaccount: bool) -> str | None:
    backend = _get_backend()
    return backend(use_pro_subaccount).get_contact_url(contact_email)


def get_raw_contact_data(contact_email: str, use_pro_subaccount: bool) -> dict:
    """Returns all data stored by the email provider on the given contact as a raw dict"""
    backend = _get_backend()
    return backend(use_pro_subaccount).get_raw_contact_data(contact_email)


def _get_backend() -> "EmailBackend":
    return import_string(settings.EMAIL_BACKEND)


def _get_backend_from_email_data(
    data: models.TransactionalEmailData | models.TransactionalWithoutTemplateEmailData,
) -> "EmailBackend":
    # Do not send unnecessary transactional emails through Sendinblue in EHP
    if (
        (settings.IS_STAGING or settings.IS_TESTING)
        and isinstance(data, models.TransactionalEmailData)
        and not data.template.send_to_ehp
        and not FeatureToggle.SEND_ALL_EMAILS_TO_EHP.is_active()
    ):
        return import_string("pcapi.core.mails.backends.logger.LoggerBackend")

    return import_string(settings.EMAIL_BACKEND)
