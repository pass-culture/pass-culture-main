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

    def get_raw_contact_data(self, contact_email: str) -> dict:
        raise NotImplementedError()
