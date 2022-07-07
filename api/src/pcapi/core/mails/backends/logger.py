from dataclasses import asdict
import logging
import typing

from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalEmailData
from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalWithoutTemplateEmailData


logger = logging.getLogger(__name__)
from ..models.models import MailResult
from .base import BaseBackend


class LoggerBackend(BaseBackend):
    """A backend that logs e-mail instead of sending it.
    It should be used for local development, and on testing/staging
    when performing load tests when we don't want to overload Sendinblue.
    """

    def send_mail(
        self,
        recipients: typing.Iterable[str],
        data: SendinblueTransactionalEmailData | SendinblueTransactionalWithoutTemplateEmailData,
    ) -> MailResult:
        recipients = ", ".join(recipients)
        sent_data = asdict(data)
        logger.info("An e-mail would be sent via Sendinblue to=%s: %s", recipients, sent_data)
        result = MailResult(sent_data=sent_data, successful=True)

        return result
