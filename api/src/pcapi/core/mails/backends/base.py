from typing import Iterable

from .. import models


class BaseBackend:
    def send_mail(
        self,
        recipients: Iterable,
        data: models.TransactionalEmailData | models.TransactionalWithoutTemplateEmailData,
    ) -> models.MailResult:
        raise NotImplementedError()
