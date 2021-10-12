from dataclasses import asdict
from datetime import date
import logging
import typing
from typing import Iterable

from requests import Response

from pcapi import settings
from pcapi.core.mails.models import MailResult
from pcapi.core.mails.transactional.sendinblue_template_ids import SendinblueTransactionalEmailData
from pcapi.tasks.sendinblue_tasks import send_transactional_email_task
from pcapi.tasks.serialization.sendinblue_tasks import SendTransactionalEmailRequest

from .base import BaseBackend


logger = logging.getLogger(__name__)


class SendinblueBackend(BaseBackend):
    def _send(self, recipients: Iterable, data: typing.Union[SendinblueTransactionalEmailData, dict]) -> MailResult:
        if isinstance(data, dict):
            raise ValueError(f"Tried sending an email via sendinblue, but received incorrectly formatted data: {data}")

        payload = SendTransactionalEmailRequest(
            recipients=recipients, template_id=data.template.id, params=data.params, tags=data.template.tags
        )
        send_transactional_email_task.delay(payload)
        return MailResult(sent_data=asdict(data), successful=True)

    def create_contact(self, email: str) -> Response:
        pass

    def update_contact(self, email: str, *, birth_date: date, department: str) -> Response:
        pass

    def add_contact_to_list(self, email: str, list_id: str) -> Response:
        pass


class ToDevSendinblueBackend(SendinblueBackend):
    def send_mail(self, recipients: Iterable, data: typing.Union[SendinblueTransactionalEmailData, dict]) -> MailResult:
        recipients = [settings.DEV_EMAIL_ADDRESS]
        return super().send_mail(recipients=recipients, data=data)
