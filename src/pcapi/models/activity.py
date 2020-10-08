from pcapi.models.db import versioning_manager


def load_activity():
    return versioning_manager.activity_cls
