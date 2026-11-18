import typing

from pcapi import settings
from pcapi.core.users.sessions import install_backoffice_login
from pcapi.flask_integration.common import AppBuilder
from pcapi.flask_integration.utils import build_app
from pcapi.routes import middlewares
from pcapi.routes.backoffice.utils import static as static_utils
from pcapi.utils.metrics import setup_metrics


if typing.TYPE_CHECKING:
    from flask import Flask


class BackofficeAppBuilder(AppBuilder):
    def after_app_creation(self, app: "Flask") -> None:
        super().after_app_creation(app)
        app.config["SESSION_COOKIE_HTTPONLY"] = True
        app.config["SESSION_COOKIE_SECURE"] = settings.SESSION_COOKIE_SECURE
        app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
        app.config["SESSION_COOKIE_NAME"] = "bo_session"
        app.config["REMEMBER_COOKIE_HTTPONLY"] = True
        app.config["REMEMBER_COOKIE_SECURE"] = settings.SESSION_COOKIE_SECURE
        app.config["REMEMBER_COOKIE_DURATION"] = 120 * 60
        app.config["REMEMBER_COOKIE_NAME"] = "bo_remember_me"
        app.config["PERMANENT_SESSION_LIFETIME"] = 120 * 60
        app.config["USE_GLOBAL_ATOMIC"] = True
        app.config["NAME"] = settings.BACKOFFICE_APP_NAME

    def install_middleware(self, app: "Flask") -> None:
        super().install_middleware(app)
        app.after_request(middlewares.add_headers)

    def install_handlers(self, app: "Flask") -> None:
        super().install_handlers(app)
        # FIXME manage error handlers like the middlewares
        import pcapi.routes.backoffice.error_handlers  # noqa F401

    def install_routes(self, app: "Flask") -> None:
        super().install_routes(app)
        from pcapi.routes.backoffice import install_routes
        from pcapi.routes.backoffice.blueprint import backoffice

        install_routes(app)
        app.register_blueprint(backoffice)

    def finalize_startup(self, app: "Flask") -> None:
        super().finalize_startup(app)
        static_utils.generate_bundles()
        install_backoffice_login()
        setup_metrics(app)


def create_app() -> "Flask":
    return build_app(BackofficeAppBuilder())
