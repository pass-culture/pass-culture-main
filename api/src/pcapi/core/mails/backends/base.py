from typing import Iterable

from .. import models


class BaseBackend:
    def send_mail(
        self,
        recipients: Iterable,
        data: models.SendinblueTransactionalEmailData | models.SendinblueTransactionalWithoutTemplateEmailData,
    ) -> models.MailResult:
        raise NotImplementedError()
