from dataclasses import asdict
from datetime import date
import logging
import typing

from requests import Response

from pcapi.core.mails.transactional.sendinblue_template_ids import SendinblueTransactionalEmailData


logger = logging.getLogger(__name__)

from ..models import MailResult
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
        else:
            mail_server = "Mailjet"
        recipients = ", ".join(recipients)
        logger.info("An e-mail would be sent via %s to=%s: %s", mail_server, recipients, data)
        result = MailResult(sent_data=data, successful=True)

        return result

    def create_contact(self, email: str) -> Response:
        logger.info("Creating contact for email=%s", email)
        response = Response()
        response.status_code = 200
        return response

    def update_contact(self, email: str, *, birth_date: date, department: str) -> Response:
        logger.info("Updating contact information for email=%s", email)
        response = Response()
        response.status_code = 200
        return response

    def add_contact_to_list(self, email: str, list_id: str) -> Response:
        logger.info("Adding email=%s to list=%s", email, list_id)
        response = Response()
        response.status_code = 200
        return response
