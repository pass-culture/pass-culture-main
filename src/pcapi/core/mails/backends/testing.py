from datetime import datetime
from typing import Iterable

from requests import Response

from .. import testing
from ..models import MailResult
from .base import BaseBackend


class TestingBackend(BaseBackend):
    """A backend that stores e-mail in a global Python list that is
    accessible from tests.
    """

    def _send(self, recipients: Iterable[str], data: dict) -> MailResult:
        data["To"] = ", ".join(recipients)
        result = MailResult(sent_data=data, successful=True)
        testing.outbox.append(result)
        return result

    def create_contact(self, email: str) -> Response:
        response = Response()
        response.status_code = 200
        return response

    def update_contact(self, email: str, *, birth_date: datetime, department: str) -> Response:
        response = Response()
        response.status_code = 200
        return response

    def add_contact_to_list(self, email: str, list_id: str) -> Response:
        response = Response()
        response.status_code = 200
        return response


class FailingBackend(BaseBackend):
    """A backend that... fails to send an e-mail."""

    def _send(self, recipients: Iterable[str], data: dict) -> MailResult:
        data["To"] = ", ".join(recipients)
        return MailResult(sent_data=data, successful=False)

    def create_contact(self, email: str) -> Response:
        response = Response()
        response.status_code = 400
        return response

    def update_contact(self, email: str, *, birth_date: datetime, department: str) -> Response:
        response = Response()
        response.status_code = 400
        return response

    def add_contact_to_list(self, email: str, list_id: str) -> Response:
        response = Response()
        response.status_code = 400
        return response
