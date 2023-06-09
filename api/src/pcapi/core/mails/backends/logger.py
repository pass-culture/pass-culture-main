from dataclasses import asdict
import logging
import typing

from pcapi.tasks.serialization import sendinblue_tasks

from .. import models
from .base import BaseBackend


logger = logging.getLogger(__name__)


class LoggerBackend(BaseBackend):
    """A backend that logs email instead of sending it.
    It should be used for local development, and on testing/staging
    when performing load tests when we don't want to overload Sendinblue.
    """

    def send_mail(
        self,
        recipients: typing.Iterable[str],
        data: models.TransactionalEmailData | models.TransactionalWithoutTemplateEmailData,
        bcc_recipients: typing.Iterable[str] = None,
    ) -> models.MailResult:
        recipients = ", ".join(recipients)
        if bcc_recipients:
            bcc_recipients = ", ".join(bcc_recipients)
        sent_data = asdict(data)
        logger.info("An email would be sent via Sendinblue to=%s, bcc=%s: %s", recipients, bcc_recipients, sent_data)
        result = models.MailResult(sent_data=sent_data, successful=True)

        return result

    def create_contact(self, payload: sendinblue_tasks.UpdateSendinblueContactRequest) -> None:
        logger.info(
            "A request to Sendinblue Contact API would be sent for user %s with attributes %s emailBlacklisted: %s",
            payload.email,
            payload.attributes,
            payload.emailBlacklisted,
        )
