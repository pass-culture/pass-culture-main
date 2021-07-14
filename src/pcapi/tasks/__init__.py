from flask import Flask


def install_handlers(app: Flask) -> None:
    # pylint: disable=unused-import
    from . import account
    from . import sendinblue_tasks
