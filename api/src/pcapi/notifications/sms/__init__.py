from pcapi import settings
from pcapi.utils.module_loading import import_string


def send_transactional_sms(recipient: str, content: str) -> None:
    backend = import_string(settings.SMS_NOTIFICATION_BACKEND)
    backend().send_transactional_sms(recipient, content)
