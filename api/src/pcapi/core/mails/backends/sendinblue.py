from dataclasses import asdict
import logging
import typing
from typing import Iterable

from pcapi import settings
from pcapi.core.mails.models import MailResult
from pcapi.core.mails.transactional.sendinblue_template_ids import SendinblueTransactionalEmailData
from pcapi.tasks.sendinblue_tasks import send_transactional_email_primary_task
from pcapi.tasks.sendinblue_tasks import send_transactional_email_secondary_task
from pcapi.tasks.serialization.sendinblue_tasks import SendTransactionalEmailRequest

from .base import BaseBackend


logger = logging.getLogger(__name__)


class SendinblueBackend(BaseBackend):
    def _send(
        self,
        recipients: Iterable,
        data: typing.Union[SendinblueTransactionalEmailData, dict],
    ) -> MailResult:
        if isinstance(data, dict):
            raise ValueError(f"Tried sending an email via sendinblue, but received incorrectly formatted data: {data}")

        payload = SendTransactionalEmailRequest(
            recipients=list(recipients),
            template_id=data.template.id,
            params=data.params,
            tags=data.template.tags,
            sender=asdict(data.template.sender.value),
        )
        if data.template.use_priority_queue:
            send_transactional_email_primary_task.delay(payload)
        else:
            send_transactional_email_secondary_task.delay(payload)

        return MailResult(sent_data=asdict(data), successful=True)


class ToDevSendinblueBackend(SendinblueBackend):
    def send_mail(
        self,
        recipients: Iterable,
        data: typing.Union[SendinblueTransactionalEmailData, dict],
    ) -> MailResult:
        recipients = [settings.DEV_EMAIL_ADDRESS]
        return super().send_mail(recipients=recipients, data=data)
