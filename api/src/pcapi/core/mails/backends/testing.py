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
        bcc_recipients: Iterable[str] = None,
    ) -> models.MailResult:
        sent_data = asdict(data)
        sent_data["To"] = ", ".join(recipients)
        if bcc_recipients:
            sent_data["Bcc"] = ", ".join(bcc_recipients)
        result = models.MailResult(sent_data=sent_data, successful=True)
        testing.outbox.append(result)
        return result
