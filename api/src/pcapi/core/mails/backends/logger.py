import logging
import typing
from dataclasses import asdict

from pcapi.tasks.serialization import sendinblue_tasks

from .. import models
from .base import BaseBackend


logger = logging.getLogger(__name__)


class LoggerBackend(BaseBackend):
    """A backend that logs email instead of sending it.
    It should be used for local development, and on testing/staging
    when performing load tests when we don't want to overload Sendinblue.
    """

    def __init__(self, use_pro_subaccount: bool) -> None:
        super().__init__()
        self.use_pro_subaccount = use_pro_subaccount

    def send_mail(
        self,
        recipients: typing.Iterable[str],
        data: models.TransactionalEmailData | models.TransactionalWithoutTemplateEmailData,
        bcc_recipients: typing.Iterable[str] = (),
    ) -> None:
        recipients = ", ".join(recipients)
        if bcc_recipients:
            bcc_recipients = ", ".join(bcc_recipients)
        sent_data = asdict(data)
        logger.info(
            "An email would be sent via Sendinblue %sto=%s, bcc=%s: %s",
            "using the PRO subaccount " if self.use_pro_subaccount else "",
            recipients,
            bcc_recipients,
            sent_data,
        )

    def create_contact(self, payload: sendinblue_tasks.UpdateSendinblueContactRequest) -> None:
        logger.info(
            "A request to Sendinblue Contact %sAPI would be sent for user %s with attributes %s emailBlacklisted: %s",
            "PRO" if self.use_pro_subaccount else "",
            payload.email,
            payload.attributes,
            payload.emailBlacklisted,
        )

    def delete_contact(self, contact_email: str) -> None:
        logger.info(
            "A request to Sendinblue Contact %sAPI would be sent for user %s to delete them.",
            "PRO" if self.use_pro_subaccount else "",
            contact_email,
        )

    def get_contact_url(self, contact_email: str) -> None:
        logger.info(
            "A request to Sendinblue Contact %sAPI would be sent for user %s to to get their info.",
            "PRO" if self.use_pro_subaccount else "",
            contact_email,
        )

    def get_raw_contact_data(self, contact_email: str) -> dict:
        logger.info(
            "A request to Sendinblue Contact %sAPI would be sent for user %s to to get their raw info.",
            "PRO" if self.use_pro_subaccount else "",
            contact_email,
        )
        return {}
