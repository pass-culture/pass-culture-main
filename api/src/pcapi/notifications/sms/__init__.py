from pcapi import settings
from pcapi.utils.module_loading import import_string


def send_transactional_sms(recipient: str, content: str) -> bool:
    backend = import_string(settings.SMS_NOTIFICATION_BACKEND)
    return backend().send_transactional_sms(recipient, content)
