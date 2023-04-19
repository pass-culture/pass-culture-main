from typing import Iterable

from pcapi.core.events import backend as events_backend
from pcapi.core.mails import models
from pcapi.tasks.serialization import sendinblue_tasks


class BaseBackend(events_backend.ExternalServiceBackend):
    def send_mail(
        self,
        recipients: Iterable,
        data: models.TransactionalEmailData | models.TransactionalWithoutTemplateEmailData,
        bcc_recipients: Iterable = None,
    ) -> models.MailResult:
        raise NotImplementedError()

    def create_contact(self, payload: sendinblue_tasks.UpdateSendinblueContactRequest) -> None:
        raise NotImplementedError()

    def handle_event(self, event: events_backend.Event) -> None:
        return super().handle_event(event)
