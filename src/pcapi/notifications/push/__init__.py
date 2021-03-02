from pcapi import settings
from pcapi.utils.module_loading import import_string


def update_user_attributes(user_id: int, attribute_values: dict) -> None:
    backend = import_string(settings.PUSH_NOTIFICATION_BACKEND)
    backend().update_user_attributes(user_id, attribute_values)
