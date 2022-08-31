from dataclasses import asdict
import logging
from typing import Iterable

from pcapi import settings
from pcapi.core.users.repository import find_user_by_email
from pcapi.tasks.sendinblue_tasks import send_transactional_email_primary_task
from pcapi.tasks.sendinblue_tasks import send_transactional_email_secondary_task
from pcapi.tasks.serialization.sendinblue_tasks import SendTransactionalEmailRequest

from .. import models
from .base import BaseBackend


logger = logging.getLogger(__name__)


class SendinblueBackend(BaseBackend):
    def send_mail(
        self,
        recipients: Iterable,
        data: models.SendinblueTransactionalEmailData | models.SendinblueTransactionalWithoutTemplateEmailData,
    ) -> models.MailResult:
        if isinstance(data, models.SendinblueTransactionalEmailData):
            payload = SendTransactionalEmailRequest(
                recipients=list(recipients),
                template_id=data.template.id,
                params=data.params,
                tags=data.template.tags,
                sender=asdict(data.template.sender.value),
                reply_to=asdict(data.reply_to),  # equal to template sender if reply_to is None
                subject=None,
                html_content=None,
                attachment=None,
            )
            if data.template.use_priority_queue:
                send_transactional_email_primary_task.delay(payload)
            else:
                send_transactional_email_secondary_task.delay(payload)

        elif isinstance(data, models.SendinblueTransactionalWithoutTemplateEmailData):
            payload = SendTransactionalEmailRequest(
                recipients=list(recipients),
                sender=asdict(data.sender.value),
                subject=data.subject,
                html_content=data.html_content,
                attachment=data.attachment,
                reply_to=asdict(data.reply_to),  # equal to sender if reply_to is None
                template_id=None,
                params=None,
                tags=None,
            )
            send_transactional_email_secondary_task.delay(payload)

        else:
            raise ValueError(f"Tried sending an email via sendinblue, but received incorrectly formatted data: {data}")

        return models.MailResult(sent_data=asdict(data), successful=True)


class ToDevSendinblueBackend(SendinblueBackend):
    def send_mail(
        self,
        recipients: Iterable,
        data: models.SendinblueTransactionalEmailData | models.SendinblueTransactionalWithoutTemplateEmailData,
    ) -> models.MailResult:
        whitelisted_recipients = set()
        for recipient in recipients:
            # Imported test users are whitelisted (Internal users, Bug Bounty, audit, etc.)
            user = find_user_by_email(recipient)
            if (user and user.has_test_role) or recipient in settings.WHITELISTED_EMAIL_RECIPIENTS:
                whitelisted_recipients.add(recipient)

        if whitelisted_recipients:
            recipients = list(whitelisted_recipients)
        else:
            recipients = [settings.DEV_EMAIL_ADDRESS]
        return super().send_mail(recipients=recipients, data=data)
