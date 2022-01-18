from pcapi import settings
from pcapi.utils.module_loading import import_string


def send_internal_message() -> bool:
    backend = import_string(settings.INTERNAL_NOTIFICATION_BACKEND)
    return backend().send_internal_message()
