from flask import Flask


def install_handlers(app: Flask) -> None:
    # pylint: disable=unused-import
    from . import batch_tasks
    from . import sendinblue_tasks
    from . import ubble_tasks
