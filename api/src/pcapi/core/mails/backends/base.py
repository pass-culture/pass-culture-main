from typing import Iterable
from typing import Union

from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalEmailData
from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalWithoutTemplateEmailData

from ..models.models import MailResult


class BaseBackend:
    def send_mail(
        self,
        recipients: Iterable,
        data: Union[SendinblueTransactionalEmailData, SendinblueTransactionalWithoutTemplateEmailData],
    ) -> MailResult:
        raise NotImplementedError()
