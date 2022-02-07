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
    when performing load tests when we don't want to overload Mailjet.
    """

    def _send(
        self, recipients: typing.Iterable[str], data: typing.Union[dict, SendinblueTransactionalEmailData]
    ) -> MailResult:
        if isinstance(data, SendinblueTransactionalEmailData):
            data = asdict(data)
            mail_server = "Sendinblue"
        elif isinstance(data, SendinblueTransactionalWithoutTemplateEmailData):
            data = asdict(data)
            mail_server = "Sendinblue with no template"
        else:
            mail_server = "Mailjet"
        recipients = ", ".join(recipients)
        logger.info("An e-mail would be sent via %s to=%s: %s", mail_server, recipients, data)
        result = MailResult(sent_data=data, successful=True)

        return result
