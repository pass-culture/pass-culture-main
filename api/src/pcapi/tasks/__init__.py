from flask import Flask


def install_handlers(app: Flask) -> None:
    import pcapi.core.providers.tasks

    from . import batch_tasks, beamer_tasks, external_api_booking_notification_tasks, sendinblue_tasks, ubble_tasks
