from dataclasses import asdict
import logging
import typing

from .. import models
from .base import BaseBackend


logger = logging.getLogger(__name__)


class LoggerBackend(BaseBackend):
    """A backend that logs e-mail instead of sending it.
    It should be used for local development, and on testing/staging
    when performing load tests when we don't want to overload Sendinblue.
    """

    def send_mail(
        self,
        recipients: typing.Iterable[str],
        data: models.SendinblueTransactionalEmailData | models.SendinblueTransactionalWithoutTemplateEmailData,
    ) -> models.MailResult:
        recipients = ", ".join(recipients)
        sent_data = asdict(data)
        logger.info("An e-mail would be sent via Sendinblue to=%s: %s", recipients, sent_data)
        result = models.MailResult(sent_data=sent_data, successful=True)

        return result
