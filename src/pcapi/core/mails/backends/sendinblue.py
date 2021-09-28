from datetime import date
import logging
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
    def _send(self, recipients: Iterable, data: SendinblueTransactionalEmailData) -> MailResult:
        payload = SendTransactionalEmailRequest(
            recipients=recipients, template_id=data.template.id, params=data.params, tags=data.template.tags
        )
        send_transactional_email_task.delay(payload)
        return MailResult(sent_data=data.__dict__(), successful=True)

    def create_contact(self, email: str) -> Response:
        pass

    def update_contact(self, email: str, *, birth_date: date, department: str) -> Response:
        pass

    def add_contact_to_list(self, email: str, list_id: str) -> Response:
        pass


class ToDevSendinblueBackend(SendinblueBackend):
    def _send(self, recipients: Iterable, data: SendinblueTransactionalEmailData) -> MailResult:
        recipients = [settings.DEV_EMAIL_ADDRESS]
        return super().send_mail(recipients=recipients, data=data)
