import typing

from flask import current_app


if typing.TYPE_CHECKING:
    from flask import Flask

    from pcapi.flask_integration.app_builder.common import AppBuilder


_current_app: "Flask | None" = None


class AppAlreadyExistsError(Exception):
    pass


def build_app(builder: "AppBuilder") -> "Flask":
    builder.before_app_creation()
    app = builder.create_app()
    _register_app(app)
    builder.after_app_creation(app)
    builder.install_extensions(app)
    builder.install_middleware(app)
    with app.app_context():
        builder.install_routes(app)
        builder.install_handlers(app)
        builder.finalize_startup(app)
    return app


def _register_app(app: "Flask") -> None:
    """
    register app to make it available for gunicorn.conf.py::pre_fork function
    """
    global _current_app  # noqa: PLW0603

    if _current_app:
        raise AppAlreadyExistsError("There is already an app for this worker")
    _current_app = app


def get_current_app() -> "Flask | None":
    """
    get current_app regardless of context. This function should be only called in gunicorn.conf.py::pre_fork
    """
    try:
        _ = current_app.extensions  # check if the app is initialized
        return current_app
    except RuntimeError:
        return _current_app
