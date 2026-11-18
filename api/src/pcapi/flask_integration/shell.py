import typing

from pcapi import settings
from pcapi.flask_integration.common import AppBuilder
from pcapi.flask_integration.utils import build_app
from pcapi.routes import middlewares
from pcapi.scripts.install import install_commands
from pcapi.utils.metrics import setup_metrics


if typing.TYPE_CHECKING:
    from flask import Flask


class ShellAppBuilder(AppBuilder):
    def after_app_creation(self, app: "Flask") -> None:
        super().after_app_creation(app)
        app.config["JWT_SECRET_KEY"] = settings.JWT_SECRET_KEY
        app.config["NAME"] = settings.BACKEND_APP_NAME

    def install_middleware(self, app: "Flask") -> None:
        super().install_middleware(app)
        app.shell_context_processor(middlewares.get_shell_extra_context)

    def install_routes(self, app: "Flask") -> None:
        super().install_routes(app)
        install_commands(app)

    def finalize_startup(self, app: "Flask") -> None:
        super().finalize_startup(app)
        setup_metrics(app)


def create_app() -> "Flask":
    return build_app(ShellAppBuilder())
