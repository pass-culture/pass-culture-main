from typing import Iterable

from pcapi.tasks.serialization import sendinblue_tasks

from .. import models


class BaseBackend:
    def send_mail(
        self,
        recipients: Iterable,
        data: models.TransactionalEmailData | models.TransactionalWithoutTemplateEmailData,
        bcc_recipients: Iterable = None,
    ) -> models.MailResult:
        raise NotImplementedError()

    def create_contact(self, payload: sendinblue_tasks.UpdateSendinblueContactRequest) -> None:
        raise NotImplementedError()
