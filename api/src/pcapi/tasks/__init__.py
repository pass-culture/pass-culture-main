from flask import Flask


def install_handlers(app: Flask) -> None:
    import pcapi.core.providers.tasks

    from . import batch_tasks
    from . import beamer_tasks
    from . import external_api_booking_notification_tasks
    from . import sendinblue_tasks
    from . import ubble_tasks
