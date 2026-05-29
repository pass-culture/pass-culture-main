from flask import Flask


def install_handlers(app: Flask) -> None:
    import pcapi.core.providers.tasks
