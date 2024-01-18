from dataclasses import asdict
from typing import Iterable

from pcapi.core.users import testing as users_testing
from pcapi.tasks.serialization import sendinblue_tasks

from .. import models
from .. import testing
from .base import BaseBackend


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
