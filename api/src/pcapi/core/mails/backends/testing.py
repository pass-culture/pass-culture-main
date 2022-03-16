from dataclasses import asdict
from typing import Iterable
from typing import Union

from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalEmailData
from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalWithoutTemplateEmailData

from .. import testing
from ..models.models import MailResult
from .base import BaseBackend


class TestingBackend(BaseBackend):
    """A backend that stores e-mail in a global Python list that is
    accessible from tests.
    """

    def _send(
        self,
        recipients: Iterable[str],
        data: Union[SendinblueTransactionalEmailData, SendinblueTransactionalWithoutTemplateEmailData, dict],
    ) -> MailResult:
        if not isinstance(data, dict):
            data = asdict(data)
        data["To"] = ", ".join(recipients)
        result = MailResult(sent_data=data, successful=True)
        testing.outbox.append(result)
        return result


class FailingBackend(BaseBackend):
    """A backend that... fails to send an e-mail."""

    def _send(
        self,
        recipients: Iterable[str],
        data: Union[SendinblueTransactionalEmailData, SendinblueTransactionalWithoutTemplateEmailData, dict],
    ) -> MailResult:
        data["To"] = ", ".join(recipients)
        return MailResult(sent_data=data, successful=False)
