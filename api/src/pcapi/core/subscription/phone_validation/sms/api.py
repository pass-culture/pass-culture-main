import typing

from pcapi import settings
from pcapi.core.subscription.phone_validation.sms.backends.logger import LoggerBackend
from pcapi.core.subscription.phone_validation.sms.backends.sendinblue import SendinblueBackend
from pcapi.core.subscription.phone_validation.sms.backends.sendinblue import ToDevSendinblueBackend
from pcapi.core.subscription.phone_validation.sms.backends.testing import TestingBackend


type Backend = SendinblueBackend | ToDevSendinblueBackend | LoggerBackend | TestingBackend
BACKEND_BY_KEY: typing.Final[dict[str, type[Backend]]] = {
    "SendinblueBackend": SendinblueBackend,
    "ToDevSendinblueBackend": ToDevSendinblueBackend,
    "LoggerBackend": LoggerBackend,
    "TestingBackend": TestingBackend,
    "pcapi.notifications.sms.backends.sendinblue.ToDevSendinblueBackend": ToDevSendinblueBackend,
    "pcapi.notifications.sms.backends.sendinblue.SendinblueBackend": SendinblueBackend,
}


def _get_backend() -> Backend:
    return BACKEND_BY_KEY[settings.SMS_NOTIFICATION_BACKEND]()


def send_transactional_sms(recipient: str, content: str) -> None:
    _get_backend().send_transactional_sms(recipient, content)
