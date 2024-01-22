from dataclasses import asdict
from typing import Iterable
import uuid

from pcapi.core.mails.transactional.send_transactional_email import save_message_ids_for_scheduled_emails
from pcapi.core.users import testing as users_testing
from pcapi.tasks.serialization import sendinblue_tasks

from .. import models
from .. import testing
from .base import BaseBackend


class FakeResponse:
    def __init__(self, status_code: int = 202) -> None:
        self.status_code = status_code

    def json(self) -> dict:
        return {"messageId": str(uuid.uuid4())}


def get_payload_from_data(
    recipients: Iterable[str],
    data: models.TransactionalEmailData | models.TransactionalWithoutTemplateEmailData,
    bcc_recipients: Iterable[str] = (),
) -> sendinblue_tasks.SendTransactionalEmailRequest:
    recipients = list(recipients)
    bcc_recipients = list(bcc_recipients)
    reply_to = asdict(data.reply_to)  # equal to sender if reply_to is None
    scheduled_at = data.scheduled_at
    if isinstance(data, models.TransactionalEmailData):
        return sendinblue_tasks.SendTransactionalEmailRequest(
            attachment=None,
            bcc_recipients=bcc_recipients,
            html_content=None,
            params=data.params,
            recipients=recipients,
            reply_to=reply_to,
            scheduled_at=scheduled_at,
            sender=asdict(data.template.sender.value),
            subject=None,
            tags=data.template.tags,
            template_id=data.template.id,
        )

    if isinstance(data, models.TransactionalWithoutTemplateEmailData):
        return sendinblue_tasks.SendTransactionalEmailRequest(
            attachment=asdict(data.attachment) if data.attachment else None,
            bcc_recipients=bcc_recipients,
            html_content=data.html_content,
            params=None,
            recipients=recipients,
            reply_to=reply_to,
            scheduled_at=scheduled_at,
            sender=asdict(data.sender.value),
            subject=data.subject,
            tags=None,
            template_id=None,
        )

    raise ValueError()


class TestingBackend(BaseBackend):
    """A backend that stores email in a global Python list that is
    accessible from tests.
    """

    def send_mail(
        self,
        recipients: Iterable[str],
        data: models.TransactionalEmailData | models.TransactionalWithoutTemplateEmailData,
        bcc_recipients: Iterable[str] = (),
    ) -> None:
        response = FakeResponse()
        payload = get_payload_from_data(recipients, data, bcc_recipients)
        save_message_ids_for_scheduled_emails(response, payload=payload)

        sent_data = asdict(data)
        sent_data["To"] = ", ".join(recipients)
        if bcc_recipients:
            sent_data["Bcc"] = ", ".join(bcc_recipients)
        testing.outbox.append(sent_data)

    def create_contact(self, payload: sendinblue_tasks.UpdateSendinblueContactRequest) -> None:
        users_testing.sendinblue_requests.append(
            {"email": payload.email, "attributes": payload.attributes, "emailBlacklisted": payload.emailBlacklisted}
        )

    def delete_contact(self, contact_email: str) -> None:
        users_testing.sendinblue_requests.append({"email": contact_email, "action": "delete"})

    def get_contact_url(self, contact_email: str) -> str | None:
        users_testing.sendinblue_requests.append({"email": contact_email, "action": "get_contact_url"})
        return None

    def cancel_scheduled_email(self, message_id: str) -> None:
        users_testing.sendinblue_requests.append({"messageId": message_id, "action": "cancel"})
