from pcapi import settings
from pcapi.utils.module_loading import import_string


def send_internal_message(channel: str, blocks, icon_emoji: str):
    backend = import_string(settings.INTERNAL_NOTIFICATION_BACKEND)
    backend().send_internal_message(channel, blocks, icon_emoji)
