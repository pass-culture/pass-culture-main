from dataclasses import asdict
from typing import Iterable

from pcapi.tasks.serialization import sendinblue_tasks

from .. import models


class BaseBackend:
    def send_mail(
        self,
        recipients: Iterable,
        data: models.TransactionalEmailData | models.TransactionalWithoutTemplateEmailData,
        bcc_recipients: Iterable[str] = (),
    ) -> None:
        raise NotImplementedError()

    def create_contact(self, payload: sendinblue_tasks.UpdateSendinblueContactRequest) -> None:
        raise NotImplementedError()

    def delete_contact(self, contact_email: str) -> None:
        raise NotImplementedError()

    def get_contact_url(self, contact_email: str) -> str | None:
        raise NotImplementedError()

    def cancel_scheduled_email(self, message_id: str) -> None:
        raise NotImplementedError()

    def get_payload_from_data(
        self,
        recipients: Iterable[str],
        data: models.TransactionalEmailData | models.TransactionalWithoutTemplateEmailData,
        bcc_recipients: Iterable[str] = (),
    ) -> tuple[sendinblue_tasks.SendTransactionalEmailRequest, bool]:
        recipients = list(recipients)
        bcc_recipients = list(bcc_recipients)
        reply_to = asdict(data.reply_to)  # equal to sender if reply_to is None
        scheduled_at = data.scheduled_at
        if isinstance(data, models.TransactionalEmailData):
            use_priority_queue = data.template.use_priority_queue
            return (
                sendinblue_tasks.SendTransactionalEmailRequest(
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
                ),
                use_priority_queue,
            )

        if isinstance(data, models.TransactionalWithoutTemplateEmailData):
            return (
                sendinblue_tasks.SendTransactionalEmailRequest(
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
                ),
                False,
            )

        raise ValueError(f"Tried sending an email via sendinblue, but received incorrectly formatted data: {data}")
