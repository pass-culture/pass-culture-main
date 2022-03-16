from typing import Iterable
from typing import Union

from pcapi import settings
from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalEmailData
from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalWithoutTemplateEmailData

from ..models.models import MailResult


class BaseBackend:
    def send_mail(
        self,
        recipients: Iterable[str],
        data: Union[SendinblueTransactionalEmailData, SendinblueTransactionalWithoutTemplateEmailData, dict],
    ) -> MailResult:
        if isinstance(data, dict):  # for mailjet
            data.setdefault("FromEmail", settings.SUPPORT_EMAIL_ADDRESS)
            if "Vars" in data:
                data["Vars"].setdefault("env", "" if settings.IS_PROD else f"-{settings.ENV}")
            return self._send(recipients=recipients, data=data)

        return self._send(recipients=recipients, data=data)

    def _send(
        self,
        recipients: Iterable,
        data: Union[SendinblueTransactionalEmailData, SendinblueTransactionalWithoutTemplateEmailData, dict],
    ) -> MailResult:
        raise NotImplementedError()
