from datetime import date
from typing import Iterable
from typing import Union

from requests import Response

from pcapi import settings
from pcapi.core.mails.transactional.sendinblue_template_ids import SendinblueTransactionalEmailData

from ..models import MailResult


class BaseBackend:
    def send_mail(self, recipients: Iterable[str], data: Union[SendinblueTransactionalEmailData, dict]) -> MailResult:
        if isinstance(data, dict):  # for mailjet
            data.setdefault("FromEmail", settings.SUPPORT_EMAIL_ADDRESS)
            if "Vars" in data:
                data["Vars"].setdefault("env", "" if settings.IS_PROD else f"-{settings.ENV}")

        return self._send(recipients=recipients, data=data)

    def _send(self, recipients: Iterable, data: Union[SendinblueTransactionalEmailData, dict]) -> MailResult:
        raise NotImplementedError()

    def create_contact(self, email: str) -> Response:
        raise NotImplementedError()

    def update_contact(self, email: str, *, birth_date: date, department: str) -> Response:
        raise NotImplementedError()

    def add_contact_to_list(self, email: str, list_id: str) -> Response:
        raise NotImplementedError()
