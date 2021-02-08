from datetime import date
from typing import Iterable

from requests import Response

from pcapi import settings
from pcapi.utils.module_loading import import_string

from . import models


class MailServiceException(Exception):
    pass


def send(*, recipients: Iterable[str], data: dict) -> bool:
    """Try to send an e-mail and return whether it was successful."""
    if isinstance(recipients, str):
        if settings.IS_RUNNING_TESTS:
            raise ValueError("Recipients should be a sequence, not a single string.")
        recipients = [recipients]
    backend = import_string(settings.EMAIL_BACKEND)
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


# FIXME (dbaty, 2020-02-02): returning a Response object is not very
# friendly. Could we not return a boolean instead? Ditto for other
# functions below.
def create_contact(email: str) -> Response:
    backend = import_string(settings.EMAIL_BACKEND)
    return backend().create_contact(email)


def update_contact(email: str, *, birth_date: date, department: str) -> Response:
    backend = import_string(settings.EMAIL_BACKEND)
    return backend().update_contact(email, birth_date=birth_date, department=department)


def add_contact_to_list(email: str, list_id: str) -> Response:
    backend = import_string(settings.EMAIL_BACKEND)
    return backend().add_contact_to_list(email, list_id)
