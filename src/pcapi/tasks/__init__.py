from flask import Flask


def install_handlers(app: Flask) -> None:
    # pylint: disable=unused-import
    from .void_task import void_task
