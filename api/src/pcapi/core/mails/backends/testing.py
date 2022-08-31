from dataclasses import asdict
from typing import Iterable

from .. import models
from .. import testing
from .base import BaseBackend


class TestingBackend(BaseBackend):
    """A backend that stores e-mail in a global Python list that is
    accessible from tests.
    """

    def send_mail(
        self,
        recipients: Iterable[str],
        data: models.TransactionalEmailData | models.TransactionalWithoutTemplateEmailData,
    ) -> models.MailResult:
        sent_data = asdict(data)
        sent_data["To"] = ", ".join(recipients)
        result = models.MailResult(sent_data=sent_data, successful=True)
        testing.outbox.append(result)
        return result


class FailingBackend(BaseBackend):
    """A backend that... fails to send an e-mail."""

    def send_mail(
        self,
        recipients: Iterable[str],
        data: models.TransactionalEmailData | models.TransactionalWithoutTemplateEmailData,
    ) -> models.MailResult:
        sent_data = asdict(data)
        sent_data["To"] = ", ".join(recipients)
        return models.MailResult(sent_data=sent_data, successful=False)
