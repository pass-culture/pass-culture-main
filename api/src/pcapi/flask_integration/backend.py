import typing

from flask_jwt_extended import JWTManager

from pcapi import settings
from pcapi.core.users.sessions import install_routed_login
from pcapi.flask_integration.common import AppBuilder
from pcapi.flask_integration.utils import build_app
from pcapi.routes import install_all_routes
from pcapi.scripts.install import install_commands
from pcapi.utils.metrics import setup_metrics


if typing.TYPE_CHECKING:
    from flask import Flask


class BackendAppBuilder(AppBuilder):
    def after_app_creation(self, app: "Flask") -> None:
        super().after_app_creation(app)
        app.config["SESSION_COOKIE_HTTPONLY"] = True
        app.config["SESSION_COOKIE_SECURE"] = settings.SESSION_COOKIE_SECURE
        app.config["SESSION_COOKIE_SAMESITE"] = settings.SESSION_COOKIE_SAMESITE
        app.config["REMEMBER_COOKIE_HTTPONLY"] = True
        app.config["REMEMBER_COOKIE_SECURE"] = settings.SESSION_COOKIE_SECURE
        app.config["REMEMBER_COOKIE_DURATION"] = 90 * 24 * 3600
        app.config["PERMANENT_SESSION_LIFETIME"] = 90 * 24 * 3600
        app.config["JWT_SECRET_KEY"] = settings.JWT_SECRET_KEY
        app.config["JWT_ACCESS_TOKEN_EXPIRES"] = settings.JWT_ACCESS_TOKEN_EXPIRES
        # CSRF is disabled by default because it's used nowhere in the API except for the discord signin page.
        # The SigninForm in charge of gathering the username/password has the csrf protection explicitly activated
        # cf. pcapi.routes.discord.forms.forms.SigninForm used by this endpoint : `/auth/discord/signin`
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["USE_GLOBAL_ATOMIC"] = False
        app.config["NAME"] = settings.BACKEND_APP_NAME

    def install_extensions(self, app: "Flask") -> None:
        super().install_extensions(app)
        JWTManager(app)

    def install_routes(self, app: "Flask") -> None:
        super().install_routes(app)
        install_all_routes(app)
        install_commands(app)  # FIXME  remove commands from this buiilder and move tests to a new app

    def finalize_startup(self, app: "Flask") -> None:
        super().finalize_startup(app)
        install_routed_login()
        setup_metrics(app)


def create_app() -> "Flask":
    return build_app(BackendAppBuilder())
