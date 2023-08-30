from flask import Flask


def install_handlers(app: Flask) -> None:
    # pylint: disable=unused-import
    import pcapi.core.providers.tasks

    from . import batch_tasks
    from . import sendinblue_tasks
    from . import ubble_tasks
    from . import beamer_tasks
