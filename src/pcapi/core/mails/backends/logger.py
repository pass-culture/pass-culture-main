from datetime import date
from typing import Iterable

from requests import Response

from pcapi.utils.logger import logger

from ..models import MailResult
from .base import BaseBackend


class LoggerBackend(BaseBackend):
    """A backend that logs e-mail instead of sending it.

    It should be used for local development, and on testing/staging
    when performing load tests when we don't want to overload Mailjet.
    """

    def _send(self, recipients: Iterable[str], data: dict) -> MailResult:
        data["To"] = ", ".join(recipients)
        logger.info("An e-mail would be sent to=%s: %s", data["To"], data)
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
